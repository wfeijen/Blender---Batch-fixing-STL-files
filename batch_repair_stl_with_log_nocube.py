import bpy
import bmesh
import os

# =========================================================
# ORDNER ANPASSEN
# =========================================================

input_folder = (
    "/home/willem/Documents/3d Printen/3D modellen/WH40K/terein/1 ruine/printklaar_stl"
)

output_folder = (
    "/home/willem/Documents/3d Printen/3D modellen/WH40K/terein/1 ruine/Print_ready"
)

# =========================================================
# OUTPUT ORDNER + LOGFILE
# =========================================================

os.makedirs(output_folder, exist_ok=True)

log_file = os.path.join(output_folder, "repair_log.txt")

# =========================================================
# NON-MANIFOLD CHECK
# =========================================================


def has_non_manifold(obj):

    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.mode_set(mode="EDIT")

    bm = bmesh.from_edit_mesh(obj.data)

    non_manifold_edges = [e for e in bm.edges if not e.is_manifold]

    count = len(non_manifold_edges)

    bpy.ops.object.mode_set(mode="OBJECT")

    return count


# =========================================================
# REMOVE DOUBLES VIA BMESH
# =========================================================


def remove_doubles_bmesh(obj, distance=0.0001):

    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.mode_set(mode="EDIT")

    bm = bmesh.from_edit_mesh(obj.data)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=distance)

    bmesh.update_edit_mesh(obj.data)

    bpy.ops.object.mode_set(mode="OBJECT")


# =========================================================
# REPAIR STL
# =========================================================


def repair_stl(in_file, out_file, log):

    # -----------------------------------------------------
    # SCENE CLEANUP
    # -----------------------------------------------------

    bpy.ops.object.select_all(action="SELECT")

    bpy.ops.object.delete(use_global=False)

    print(f"\n🔧 Bearbeite: {in_file}")

    log.write(f"\n🔧 Bearbeite: {in_file}\n")

    log.flush()

    # -----------------------------------------------------
    # STL IMPORT
    # -----------------------------------------------------

    bpy.ops.wm.stl_import(filepath=in_file)

    imported_objects = bpy.context.selected_objects

    if not imported_objects:
        raise Exception("Keine Objekte importiert")

    obj = imported_objects[0]

    if obj.type != "MESH":
        raise Exception("Importiertes Objekt ist kein MESH")

    bpy.context.view_layer.objects.active = obj

    # -----------------------------------------------------
    # REMOVE DOUBLES
    # -----------------------------------------------------

    try:
        remove_doubles_bmesh(obj)

        print("  ✓ remove_doubles ok")

        log.write("  ✓ remove_doubles ok\n")

        log.flush()

    except Exception as e:
        print(f"  ❌ remove_doubles Fehler: {e}")

        log.write(f"  ❌ remove_doubles Fehler: {e}\n")

        log.flush()

    # -----------------------------------------------------
    # NON-MANIFOLD CHECK
    # -----------------------------------------------------

    non_manifold_count = has_non_manifold(obj)

    if non_manifold_count > 0:
        print(f"  ⚠ {non_manifold_count} Non-Manifold-Edges gefunden")

        log.write(f"  ⚠ {non_manifold_count} Non-Manifold-Edges gefunden\n")

        log.flush()

        bpy.context.view_layer.objects.active = obj

        bpy.ops.object.mode_set(mode="EDIT")

        bpy.ops.mesh.select_all(action="DESELECT")

        bpy.ops.mesh.select_non_manifold()

        # -------------------------------------------------
        # HOLES FILL
        # -------------------------------------------------

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
        print("  ✓ Keine Non-Manifold-Edges")

        log.write("  ✓ Keine Non-Manifold-Edges\n")

        log.flush()

    # -----------------------------------------------------
    # STL EXPORT
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

    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.delete()


# =========================================================
# BATCH RUN
# =========================================================

with open(log_file, "w", encoding="utf-8") as log:
    stl_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".stl")]

    print(f"\n📦 {len(stl_files)} STL-Dateien gefunden\n")

    for filename in stl_files:
        in_file = os.path.join(input_folder, filename)

        base, ext = os.path.splitext(filename)

        fixed_name = base + "_fixed" + ext

        out_file = os.path.join(output_folder, fixed_name)

        try:
            repair_stl(in_file, out_file, log)

        except Exception as e:
            print(f"\n❌ Fehler bei {filename}: {e}")

            log.write(f"\n❌ Fehler bei {filename}: {e}\n")

            log.flush()

print("\n🎉 Batch-Fix abgeschlossen")

print(f"📄 Logfile: {log_file}")
