import bpy
import bmesh
import os

# =========================================================
# Parameters
# =========================================================
doubles_distance = 0.0001  # Threshold for remove_doubles
simplify_ratio = 0.5  # Ratio for decimate modifier (0.5 = 50% reduction)



input_folder = (
    "/home/willem/Documents/3d Printen/3D modellen/WH40K/terein/1 ruine/printklaar_stl"
)

output_folder = (
    "/home/willem/Documents/3d Printen/3D modellen/WH40K/terein/1 ruine/Print_ready"
)

os.makedirs(output_folder, exist_ok=True)

log_file = os.path.join(output_folder, "repair_log.txt")

# =========================================================
# REMOVE DOUBLES (BMESH - SAFE)
# =========================================================


def remove_doubles(obj, distance):

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")

    bm = bmesh.from_edit_mesh(obj.data)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=distance)

    bmesh.update_edit_mesh(obj.data)

    bpy.ops.object.mode_set(mode="OBJECT")


# =========================================================
# SIMPLIFY MESH (DECIMATE)
# =========================================================


def simplify_mesh(obj, ratio):

    bpy.context.view_layer.objects.active = obj

    mod = obj.modifiers.new(name="Decimate", type="DECIMATE")
    mod.ratio = ratio

    bpy.ops.object.modifier_apply(modifier=mod.name)


# =========================================================
# NON-MANIFOLD CHECK
# =========================================================


def has_non_manifold(obj):

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")

    bm = bmesh.from_edit_mesh(obj.data)

    count = sum(1 for e in bm.edges if not e.is_manifold)

    bpy.ops.object.mode_set(mode="OBJECT")

    return count


# =========================================================
# MAIN REPAIR FUNCTION
# =========================================================


def repair_stl(in_file, out_file, log):

    # -----------------------------------------------------
    # Clear scene
    # -----------------------------------------------------

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    print(f"\n🔧 Bearbeite: {in_file}")
    log.write(f"\n🔧 Bearbeite: {in_file}\n")
    log.flush()

    # -----------------------------------------------------
    # IMPORT STL (Blender 5.x)
    # -----------------------------------------------------

    bpy.ops.wm.stl_import(filepath=in_file)

    if not bpy.context.selected_objects:
        raise Exception("Keine Objekte importiert")

    obj = bpy.context.selected_objects[0]

    if obj.type != "MESH":
        raise Exception("Kein Mesh importiert")

    bpy.context.view_layer.objects.active = obj

    # -----------------------------------------------------
    # REMOVE DOUBLES
    # -----------------------------------------------------

    try:
        remove_doubles(obj, doubles_distance)

        print("  ✓ remove_doubles ok")
        log.write("  ✓ remove_doubles ok\n")
        log.flush()

    except Exception as e:
        print(f"  ❌ remove_doubles Fehler: {e}")
        log.write(f"  ❌ remove_doubles Fehler: {e}\n")
        log.flush()

    # -----------------------------------------------------
    # SIMPLIFY MESH (REDUCE FILE SIZE)
    # -----------------------------------------------------

    try:
        simplify_mesh(obj, ratio=simplify_ratio)

        print("  ✓ simplify ok (50%)")
        log.write("  ✓ simplify ok (50%)\n")
        log.flush()

    except Exception as e:
        print(f"  ❌ simplify Fehler: {e}")
        log.write(f"  ❌ simplify Fehler: {e}\n")
        log.flush()

    # -----------------------------------------------------
    # NON-MANIFOLD CHECK
    # -----------------------------------------------------

    non_manifold = has_non_manifold(obj)

    if non_manifold > 0:
        print(f"  ⚠ {non_manifold} Non-Manifold edges")
        log.write(f"  ⚠ {non_manifold} Non-Manifold edges\n")
        log.flush()

        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")

        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.select_non_manifold()

        try:
            bpy.ops.mesh.fill()

            print("  ✓ fill ok")
            log.write("  ✓ fill ok\n")
            log.flush()

        except Exception as e:
            print(f"  ❌ fill Fehler: {e}")
            log.write(f"  ❌ fill Fehler: {e}\n")
            log.flush()

        bpy.ops.object.mode_set(mode="OBJECT")

    else:
        print("  ✓ kein Non-Manifold")
        log.write("  ✓ kein Non-Manifold\n")
        log.flush()

    # -----------------------------------------------------
    # EXPORT STL
    # -----------------------------------------------------

    try:
        bpy.ops.object.select_all(action="DESELECT")

        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        bpy.ops.wm.stl_export(filepath=out_file, export_selected_objects=True)

        print(f"✅ Exportiert: {out_file}")
        log.write(f"✅ Exportiert: {out_file}\n")
        log.flush()

    except Exception as e:
        print(f"❌ Export Fehler: {e}")
        log.write(f"❌ Export Fehler: {e}\n")
        log.flush()

    # -----------------------------------------------------
    # DELETE OBJECT
    # -----------------------------------------------------

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.ops.object.delete()


# =========================================================
# BATCH RUN
# =========================================================

with open(log_file, "w", encoding="utf-8") as log:
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(".stl")]

    print(f"\n📦 {len(files)} STL files found\n")

    for filename in files:
        in_file = os.path.join(input_folder, filename)

        base, ext = os.path.splitext(filename)

        out_file = os.path.join(output_folder, base + "_fixed" + ext)

        try:
            repair_stl(in_file, out_file, log)

        except Exception as e:
            print(f"\n❌ Error in {filename}: {e}")
            log.write(f"\n❌ Error in {filename}: {e}\n")
            log.flush()

print("\n🎉 Batch complete")
print(f"📄 Logfile: {log_file}")
