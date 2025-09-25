import bpy
import os

# ==== Ordner anpassen ====
input_folder = "~/data/3D Druck/0 - Fix STL/source"
output_folder = "~/data/3D Druck/0 - Fix STL/fixed"

# Logfile anlegen
log_file = os.path.join(output_folder, "repair_log.txt")

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def has_non_manifold(obj):
    """Prüfen ob Non-Manifold-Kanten existieren"""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_non_manifold()
    sel = [v for v in obj.data.vertices if v.select]
    bpy.ops.object.mode_set(mode='OBJECT')
    return len(sel)

def repair_stl(in_file, out_file, log):
    # Szene leeren (löscht Default Cube & alte Objekte)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    print(f"🔧 Bearbeite: {in_file}")
    log.write(f"🔧 Bearbeite: {in_file}\n"); log.flush()

    # STL importieren
    bpy.ops.import_mesh.stl(filepath=in_file)
    obj = bpy.context.selected_objects[0]
    bpy.context.view_layer.objects.active = obj

    # Prüfen ob Mesh vorhanden
    if not obj.data or obj.type != 'MESH':
        print(f"❌ {in_file} enthält keine Geometrie")
        log.write(f"❌ {in_file} enthält keine Geometrie\n\n"); log.flush()
        bpy.ops.object.delete()
        return

    # In Edit Mode wechseln
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    # 1. Doppelte Vertices verschmelzen
    try:
        bpy.ops.mesh.remove_doubles()
        print("  - remove_doubles ok")
        log.write("  - remove_doubles ok\n"); log.flush()
    except:
        print("  - remove_doubles fehlgeschlagen")
        log.write("  - remove_doubles fehlgeschlagen\n"); log.flush()

    # 2. Non-Manifold prüfen und ggf. füllen
    non_manifold_count = has_non_manifold(obj)
    if non_manifold_count > 0:
        print(f"  - {non_manifold_count} Non-Manifold-Kanten gefunden")
        log.write(f"  - {non_manifold_count} Non-Manifold-Kanten gefunden\n"); log.flush()

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_non_manifold()
        try:
            bpy.ops.mesh.fill()
            print("  - fill ok")
            log.write("  - fill ok\n"); log.flush()
        except:
            print("  - fill übersprungen (keine passenden Edges)")
            log.write("  - fill übersprungen (keine passenden Edges)\n"); log.flush()
        bpy.ops.object.mode_set(mode='OBJECT')
    else:
        print("  - keine Non-Manifold-Kanten gefunden")
        log.write("  - keine Non-Manifold-Kanten gefunden\n"); log.flush()

    # 3. STL exportieren (nur dieses Objekt!)
    try:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.export_mesh.stl(filepath=out_file, use_selection=True)
        print(f"✅ Exportiert nach: {out_file}")
        log.write(f"✅ Exportiert nach: {out_file}\n\n"); log.flush()
    except:
        print("❌ Export fehlgeschlagen")
        log.write("❌ Export fehlgeschlagen\n\n"); log.flush()

    # 4. Objekt löschen, Szene bleibt leer
    bpy.ops.object.delete()

# ==== Batchlauf ====
with open(log_file, "w", encoding="utf-8") as log:
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".stl"):
            in_file = os.path.join(input_folder, filename)
            # neuen Dateinamen mit Suffix "_fixed.stl"
            base, ext = os.path.splitext(filename)
            fixed_name = base + "_fixed" + ext
            out_file = os.path.join(output_folder, fixed_name)
            try:
                repair_stl(in_file, out_file, log)
            except Exception as e:
                print(f"❌ Fehler bei {filename}: {e}")
                log.write(f"❌ Fehler bei {filename}: {e}\n\n"); log.flush()

print(f"\nBatch-Fix abgeschlossen. Logfile: {log_file}")
