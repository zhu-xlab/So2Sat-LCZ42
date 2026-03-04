#%% -*- coding: utf-8 -*-
import os
import h5py
import numpy as np
import rasterio
from rasterio.crs import CRS
from affine import Affine

# ============================================================
# Config
# ============================================================
new_root  = r'F:\TIANCHI_DATASET\TIANCHI_NEW'
geo_fname = r'training.h5'
aux_fname = r'training_geo.h5'

max_export_per_city = 5

expected_pixel_size = 10.0
pixel_tol_ratio = 0.05

out_root = os.path.join(new_root, "exports_geotiffs/training")
os.makedirs(out_root, exist_ok=True)

REBUILD_TRANSFORM_FROM_CENTER = True

# training set
city_epsg = {
    "amsterdam": 32631, "beijing": 32650, "berlin": 32633, "bogota": 32618,
    "buenosaires": 32721, "cairo": 32636, "capetown": 32734, "caracas": 32619,
    "changsha": 32649, "chicago": 32616, "cologne": 32632, "dhaka": 32646,
    "dongying": 32650, "hongkong": 32650, "islamabad": 32643, "istanbul": 32635,
    "kyoto": 32653, "lima": 32718, "lisbon": 32629, "london": 32630,
    "losangeles": 32611, "madrid": 32630, "melbourne": 32755, "milan": 32632,
    "nanjing": 32650, "newyork": 32618, "orangitown": 32618, "paris": 32631,
    "philadelphia": 32618, "qingdao": 32651, "quezon": 32651, "riodejaneiro": 32723,
    "rome": 32633, "salvador": 32724, "saopaulo": 32723, "shanghai": 32651,
    "shenzhen": 32650, "tokyo": 32654, "vancouver": 32610, "washingtondc": 32618,
    "wuhan": 32650, "zurich": 32632
}

# val and test set
# city_epsg = {
#     "guangzhou": 32649,
#     "jakarta": 32748,
#     "moscow": 32637,
#     "mumbai": 32643,
#     "munich": 32632,
#     "nairobi": 32737,
#     "sanfrancisco": 32610,
#     "santiago": 32719,
#     "sydney": 32756,
#     "tehran": 32639
# }

# ============================================================
# Helpers
# ============================================================
def norm_city_name(x) -> str:
    if isinstance(x, (bytes, np.bytes_)):
        return x.decode("utf-8", errors="ignore").strip().lower()
    return str(x).strip().lower()

def safe_name(s: str) -> str:
    return "".join([c if c.isalnum() or c in ("_", "-") else "_" for c in s])

def worldfile_to_affine(tfw6: np.ndarray) -> Affine:
    A, D, B, E, C, F = map(float, tfw6.tolist())
    return Affine(A, B, C, D, E, F)

def affine_to_worldfile_params(transform: Affine) -> np.ndarray:
    A = float(transform.a)
    B = float(transform.b)
    C = float(transform.c)
    D = float(transform.d)
    E = float(transform.e)
    F = float(transform.f)
    return np.array([A, D, B, E, C, F], dtype=np.float64)

def save_tfw(tif_path: str, tfw6: np.ndarray):
    tfw_path = os.path.splitext(tif_path)[0] + ".tfw"
    with open(tfw_path, "w", encoding="utf-8") as f:
        for v in tfw6.tolist():
            f.write(f"{float(v):.10f}\n")

def check_transform_sane(transform: Affine, expected_px: float, tol_ratio: float = 0.05):
    a = float(transform.a)
    b = float(transform.b)
    d = float(transform.d)
    e = float(transform.e)

    if not np.isfinite([a,b,d,e]).all():
        return False, f"non-finite: a={a},b={b},d={d},e={e}"

    lo = expected_px * (1 - tol_ratio)
    hi = expected_px * (1 + tol_ratio)

    if not (lo <= abs(a) <= hi):
        return False, f"|a| not ~ {expected_px}: a={a}"
    if not (lo <= abs(e) <= hi):
        return False, f"|e| not ~ {expected_px}: e={e}"
    if abs(b) > 1e-6 or abs(d) > 1e-6:
        return False, f"rotation terms not near 0: b={b}, d={d}"
    return True, f"sane: a={a}, e={e}, b={b}, d={d}"

def transform_from_center(x_center: float, y_center: float, pixel_size: float, width: int, height: int) -> Affine:
    x0 = float(x_center) - (width / 2.0) * float(pixel_size)
    y0 = float(y_center) + (height / 2.0) * float(pixel_size)
    return Affine(float(pixel_size), 0.0, x0, 0.0, -float(pixel_size), y0)

# ============================================================
# Main
# ============================================================
h5_geo_path = os.path.join(new_root, geo_fname)
h5_aux_path = os.path.join(new_root, aux_fname)

with h5py.File(h5_geo_path, "r") as f_geo, h5py.File(h5_aux_path, "r") as f_aux:
    d_sen1 = f_geo["sen1"]   # (N,H,W,C1)
    d_sen2 = f_geo["sen2"]   # (N,H,W,C2)

    d_tfw  = f_aux["tfw"]    # (N,6) worldfile order
    d_epsg = f_aux["epsg"]   # (N,1) or (N,)
    d_city = f_aux["city"] if "city" in f_aux else f_aux["cityList"]

    N = d_sen1.shape[0]
    print("Total N:", N)

    city_all = np.array(d_city[:])  # bytes
    city_all = np.array([norm_city_name(c) for c in city_all], dtype=object)
    epsg_all = np.squeeze(np.array(d_epsg[:])).astype(int)

    total_exported = 0
    total_skipped = 0

    for city in city_epsg.keys():
        city_key = city.strip().lower()
        idx = np.where(city_all == city_key)[0]
        print(f"\n=== City '{city_key}': found {len(idx)} samples ===")

        if len(idx) == 0:
            print("  [WARN] no samples for this city in aux city list.")
            continue

        idx = idx[:max_export_per_city]

        city_dir = os.path.join(out_root, safe_name(city_key))
        os.makedirs(city_dir, exist_ok=True)

        exported = 0
        skipped = 0

        for global_i in idx:
            epsg_code = int(epsg_all[global_i])

            # CRS
            try:
                crs_obj = CRS.from_epsg(epsg_code)
            except Exception as e:
                skipped += 1
                total_skipped += 1
                print(f"  [SKIP] idx={global_i} invalid EPSG:{epsg_code}. err={e}")
                continue

            # tfw -> affine
            tfw6 = np.array(d_tfw[global_i], dtype=np.float64).reshape(-1)
            if tfw6.shape[0] != 6:
                skipped += 1
                total_skipped += 1
                print(f"  [SKIP] idx={global_i} bad tfw shape: {tfw6.shape}")
                continue

            transform_raw = worldfile_to_affine(tfw6)

            # read patch
            sen1_hwc = d_sen1[global_i]
            sen2_hwc = d_sen2[global_i]
            if sen1_hwc.ndim != 3 or sen2_hwc.ndim != 3:
                skipped += 1
                total_skipped += 1
                print(f"  [SKIP] idx={global_i} bad patch shape sen1={sen1_hwc.shape}, sen2={sen2_hwc.shape}")
                continue

            H, W, C1 = sen1_hwc.shape
            _, _, C2 = sen2_hwc.shape

            # rebuild transform from center (optional)
            transform = transform_raw
            if REBUILD_TRANSFORM_FROM_CENTER:
                px = abs(float(transform_raw.a))
                x0 = float(transform_raw.c)
                y0 = float(transform_raw.f)
                x_center = x0 + (W / 2.0) * px
                y_center = y0 - (H / 2.0) * px
                transform = transform_from_center(x_center, y_center, px, W, H)

            ok, reason = check_transform_sane(transform, expected_pixel_size, pixel_tol_ratio)
            if not ok:
                skipped += 1
                total_skipped += 1
                print(f"  [SKIP] idx={global_i} transform insane: {reason} epsg={epsg_code}")
                continue

            # HWC -> CHW
            sen1_chw = np.transpose(sen1_hwc, (2, 0, 1))
            sen2_chw = np.transpose(sen2_hwc, (2, 0, 1))

            # output paths
            sen1_out = os.path.join(city_dir, f"{safe_name(city_key)}_sen1_{int(global_i)}_epsg{epsg_code}.tif")
            sen2_out = os.path.join(city_dir, f"{safe_name(city_key)}_sen2_{int(global_i)}_epsg{epsg_code}.tif")

            # write GeoTIFF
            with rasterio.open(
                sen1_out, "w",
                driver="GTiff",
                height=H, width=W,
                count=C1,
                dtype=sen1_chw.dtype,
                crs=crs_obj,
                transform=transform,
                tiled=True,
                compress="DEFLATE"
            ) as dst:
                dst.write(sen1_chw)

            with rasterio.open(
                sen2_out, "w",
                driver="GTiff",
                height=H, width=W,
                count=C2,
                dtype=sen2_chw.dtype,
                crs=crs_obj,
                transform=transform,
                tiled=True,
                compress="DEFLATE"
            ) as dst:
                dst.write(sen2_chw)

            # write matching .tfw
            tfw_out = affine_to_worldfile_params(transform)
            save_tfw(sen1_out, tfw_out)
            save_tfw(sen2_out, tfw_out)

            exported += 1
            total_exported += 1
            print(f"  [OK] idx={global_i} epsg={epsg_code} saved")

        print(f"City done: exported={exported}, skipped={skipped}")

print("\n====================================================")
print("ALL DONE.")
print(f"total_exported={total_exported}, total_skipped={total_skipped}")
print(f"Outputs saved to:\n{out_root}")
