"""
AssetManager.py — Media Inspector, Missing Media Relinker & GPU Codec Advisor (TD-MTL)

Scans all multimedia cues in the timeline:
- Detects missing media files ('MISSING' vs 'OK')
- Performs GPU Codec Advisory (flags CPU-heavy H.264/HEVC vs GPU HAP/NotchLC)
- Batch-relinks assets across directories
"""

import os

GPU_OPTIMAL_EXTS = {'.hap', '.hapq', '.mov', '.nlc', '.jpg', '.jpeg', '.png', '.tiff', '.exr'}
CPU_HEAVY_CODECS = {'.mp4', '.mkv', '.webm', '.avi'}

class AssetManager:
    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
        self.table = ownerComp.op('table_Assets')
        self._ensure_table_header()

    def _ensure_table_header(self):
        if self.table is None:
            return
        if self.table.numRows == 0:
            self.table.appendRow(['cue_name', 'layer', 'type', 'file_path', 'exists', 'status', 'gpu_friendly', 'warning'])

    def ScanAssets(self):
        """
        Scans all cues in the timeline and populates table_Assets.
        Returns (total_assets, missing_count, warnings_count).
        """
        self._ensure_table_header()
        self.table.clear()
        self._ensure_table_header()

        mlt = parent.Timeline if hasattr(parent, 'Timeline') else op('/Multi_Layer_Timeline')
        cues_comp = mlt.op('Timeline3D/Cues') if mlt else None
        if not cues_comp:
            return (0, 0, 0)

        cues = cues_comp.findChildren(tags=['CueItem'], depth=1)
        missing_count = 0
        warnings_count = 0
        total_assets = 0

        for cue in cues:
            layer = cue.par.Layer.eval() if hasattr(cue.par, 'Layer') else 0
            
            # Check Imagefile / Video
            if hasattr(cue.par, 'Imagefile'):
                img_path = str(cue.par.Imagefile.eval() or '').strip()
                if img_path:
                    total_assets += 1
                    exists = os.path.exists(img_path)
                    ext = os.path.splitext(img_path)[1].lower()
                    
                    status = 'OK' if exists else 'MISSING'
                    if not exists:
                        missing_count += 1
                        gpu_friendly = False
                        warning = 'File not found on disk'
                    else:
                        if ext in CPU_HEAVY_CODECS or (ext == '.mov' and 'hap' not in img_path.lower() and 'notch' not in img_path.lower()):
                            gpu_friendly = False
                            warning = 'CPU-decoded codec. Consider transcoding to HAP / NotchLC for 60 FPS'
                            warnings_count += 1
                        else:
                            gpu_friendly = True
                            warning = 'Optimal GPU format'

                    self.table.appendRow([cue.name, str(layer), 'Video/Image', img_path, str(exists), status, str(gpu_friendly), warning])

            # Check Audiofile
            if hasattr(cue.par, 'Audiofile'):
                aud_path = str(cue.par.Audiofile.eval() or '').strip()
                if aud_path:
                    total_assets += 1
                    exists = os.path.exists(aud_path)
                    status = 'OK' if exists else 'MISSING'
                    if not exists:
                        missing_count += 1
                        warning = 'Audio file not found'
                    else:
                        warning = 'Audio track OK'
                    self.table.appendRow([cue.name, str(layer), 'Audio', aud_path, str(exists), status, 'True', warning])

        print(f"[AssetManager] Scan complete: {total_assets} assets, {missing_count} missing, {warnings_count} codec warnings.")
        return (total_assets, missing_count, warnings_count)

    def RelinkFolder(self, search_folder: str):
        """
        Recursively searches search_folder for missing files and relinks them.
        Returns list of relinked (cue_name, old_path, new_path).
        """
        if not os.path.isdir(search_folder):
            print(f"[AssetManager] Invalid search directory: {search_folder}")
            return []

        # Index available files in search directory
        file_map = {}
        for root_dir, _, files in os.walk(search_folder):
            for f in files:
                file_map[f.lower()] = os.path.join(root_dir, f)

        relinked = []
        mlt = parent.Timeline if hasattr(parent, 'Timeline') else op('/Multi_Layer_Timeline')
        cues_comp = mlt.op('Timeline3D/Cues') if mlt else None
        if not cues_comp:
            return []

        cues = cues_comp.findChildren(tags=['CueItem'], depth=1)
        for cue in cues:
            for par_name in ['Imagefile', 'Audiofile']:
                if hasattr(cue.par, par_name):
                    old_path = str(getattr(cue.par, par_name).eval() or '').strip()
                    if old_path and not os.path.exists(old_path):
                        filename = os.path.basename(old_path).lower()
                        if filename in file_map:
                            new_path = file_map[filename]
                            setattr(cue.par, par_name, new_path)
                            relinked.append((cue.name, old_path, new_path))
                            print(f"[AssetManager] Relinked {cue.name}.{par_name} -> {new_path}")

        # Re-scan to update table
        self.ScanAssets()
        return relinked
