#!/usr/bin/env python3
"""
Ken's Rulebook Silhouette Resizer
Takes existing silhouettes and applies proper Maus-based proportional scaling
"""

import os
from PIL import Image, ImageOps
from pathlib import Path
import json

class KenRulebookResizer:
    def __init__(self):
        # Ken's Rulebook specifications
        self.maus_length_m = 10.2  # Maus reference length
        self.canvas_width = 2000   # Standard canvas width
        self.canvas_height = 1000  # Standard canvas height
        self.canvas_usage = 0.9    # 90% of canvas width for Maus
        self.baseline_position = 0.8  # 80% down canvas
        
        # Project paths
        self.project_root = Path("G:\\Claude Wargame Icon Generator\\WWII Silhouette Icon System")
        self.input_dir = self.project_root / "wwii_icons" / "silhouettes"
        self.output_dir = self.project_root / "wwii_icons" / "silhouettes" / "Resized"
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Vehicle specifications for North Africa
        self.vehicle_specs = {
            "panzer_iv_f1": {"length_m": 5.92, "display_name": "Panzer IV F1"},
            "panzer_iii_j": {"length_m": 5.52, "display_name": "Panzer III J"}, 
            "panzer_ii_f": {"length_m": 4.81, "display_name": "Panzer II F"},
            "sdkfz_222": {"length_m": 4.80, "display_name": "Sd.Kfz 222"},
            "ju_87": {"length_m": 11.00, "display_name": "Ju-87 Stuka"},
            "bf_109": {"length_m": 8.95, "display_name": "Bf-109"},
            # British vehicles for expansion
            "m3_grant": {"length_m": 5.64, "display_name": "M3 Grant"},
            "crusader_iii": {"length_m": 5.99, "display_name": "Crusader III"},
            "m3_stuart": {"length_m": 4.53, "display_name": "M3 Stuart"},
            "25pdr_gun": {"length_m": 8.10, "display_name": "25-pdr Gun"}
        }
        
    def calculate_scale_factor(self, vehicle_length_m):
        """Calculate proper scale factor based on Maus reference"""
        maus_canvas_width = self.canvas_width * self.canvas_usage
        vehicle_canvas_width = (vehicle_length_m / self.maus_length_m) * maus_canvas_width
        return vehicle_canvas_width / self.canvas_width
        
    def resize_silhouette(self, input_path, vehicle_key, output_path=None):
        """Resize a silhouette to Ken's Rulebook specifications"""
        
        if vehicle_key not in self.vehicle_specs:
            print(f"ERROR: Unknown vehicle key '{vehicle_key}'")
            print(f"Available keys: {', '.join(self.vehicle_specs.keys())}")
            return None
            
        vehicle_spec = self.vehicle_specs[vehicle_key]
        vehicle_length = vehicle_spec["length_m"]
        display_name = vehicle_spec["display_name"]
        
        print(f"Processing {display_name} ({vehicle_length}m)...")
        
        try:
            # Load existing silhouette
            silhouette = Image.open(input_path).convert("RGBA")
            print(f"  Loaded: {silhouette.size[0]}x{silhouette.size[1]} pixels")
            
            # Calculate target dimensions
            scale_factor = self.calculate_scale_factor(vehicle_length)
            target_width = int(self.canvas_width * scale_factor)
            
            # Maintain aspect ratio for height
            aspect_ratio = silhouette.size[1] / silhouette.size[0]
            target_height = int(target_width * aspect_ratio)
            
            print(f"  Target size: {target_width}x{target_height} pixels ({scale_factor:.1%} of canvas)")
            
            # Resize silhouette with high quality
            resized = silhouette.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Create Ken's Rulebook canvas (transparent background)
            canvas = Image.new("RGBA", (self.canvas_width, self.canvas_height), (0, 0, 0, 0))
            
            # Calculate position (centered horizontally, baseline aligned)
            x_pos = (self.canvas_width - target_width) // 2
            y_pos = int(self.canvas_height * self.baseline_position) - target_height
            
            # Ensure vehicle fits in canvas
            y_pos = max(0, y_pos)
            
            print(f"  Positioned at: ({x_pos}, {y_pos})")
            
            # Paste resized silhouette onto canvas
            canvas.paste(resized, (x_pos, y_pos), resized)
            
            # Generate output filename if not provided
            if output_path is None:
                output_filename = f"{display_name.replace(' ', '_').replace('.', '')}_Scaled.png"
                output_path = self.output_dir / output_filename
            
            # Save result
            canvas.save(output_path, "PNG")
            print(f"  ✅ Saved: {output_path}")
            
            # Create metadata
            metadata = {
                "vehicle": display_name,
                "length_m": vehicle_length,
                "scale_factor": scale_factor,
                "canvas_size": [self.canvas_width, self.canvas_height],
                "silhouette_size": [target_width, target_height],
                "position": [x_pos, y_pos],
                "maus_reference": self.maus_length_m,
                "ken_rulebook_compliant": True
            }
            
            metadata_path = output_path.with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return output_path
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            return None
    
    def find_existing_silhouettes(self):
        """Find all existing silhouette files"""
        patterns = ["*.png", "*.PNG"]
        found_files = []
        
        for pattern in patterns:
            found_files.extend(self.input_dir.glob(pattern))
            
        # Filter out comparison and preview files
        silhouettes = []
        for file in found_files:
            if not any(exclude in file.name for exclude in 
                      ["COMPARISON", "Counter", "preview", "_scaled", "_Scaled"]):
                silhouettes.append(file)
        
        return silhouettes
    
    def auto_detect_and_resize(self):
        """Automatically detect and resize existing silhouettes"""
        print("🔍 Scanning for existing silhouettes...")
        
        existing_files = self.find_existing_silhouettes()
        print(f"Found {len(existing_files)} potential silhouette files")
        
        processed = 0
        
        for file_path in existing_files:
            print(f"\n📁 Examining: {file_path.name}")
            
            # Try to match filename to vehicle specs
            filename_lower = file_path.name.lower()
            matched_vehicle = None
            
            # Simple pattern matching
            if "panzer_iv" in filename_lower or "pzkpfw_iv" in filename_lower:
                if "f2" in filename_lower:
                    matched_vehicle = "panzer_iv_f2"  # If we add F2 spec
                else:
                    matched_vehicle = "panzer_iv_f1"
            elif "panzer_iii" in filename_lower or "pzkpfw_iii" in filename_lower:
                matched_vehicle = "panzer_iii_j"
            elif "panzer_ii" in filename_lower or "pzkpfw_ii" in filename_lower:
                matched_vehicle = "panzer_ii_f"
            elif "222" in filename_lower:
                matched_vehicle = "sdkfz_222"
            elif "ju" in filename_lower and "87" in filename_lower:
                matched_vehicle = "ju_87"
            elif "bf" in filename_lower and "109" in filename_lower:
                matched_vehicle = "bf_109"
            
            if matched_vehicle:
                print(f"  🎯 Matched to: {self.vehicle_specs[matched_vehicle]['display_name']}")
                result = self.resize_silhouette(file_path, matched_vehicle)
                if result:
                    processed += 1
            else:
                print(f"  ⚠️ Could not match filename to vehicle database")
                print(f"     Available vehicles: {', '.join(self.vehicle_specs.keys())}")
        
        print(f"\n✅ Resized {processed} silhouettes to Ken's Rulebook standards")
        print(f"📁 Output saved to: {self.output_dir}")
        
    def resize_specific_files(self):
        """Interactive mode to resize specific files"""
        print("\n🎯 Manual File Selection Mode")
        
        existing_files = self.find_existing_silhouettes()
        
        if not existing_files:
            print("❌ No silhouette files found!")
            return
        
        print(f"\nFound {len(existing_files)} files:")
        for i, file in enumerate(existing_files, 1):
            print(f"  {i}. {file.name}")
        
        print(f"\nAvailable vehicle types:")
        for i, (key, spec) in enumerate(self.vehicle_specs.items(), 1):
            print(f"  {i}. {key} ({spec['display_name']} - {spec['length_m']}m)")
        
        try:
            file_choice = int(input(f"\nSelect file (1-{len(existing_files)}): ")) - 1
            if 0 <= file_choice < len(existing_files):
                selected_file = existing_files[file_choice]
                
                vehicle_keys = list(self.vehicle_specs.keys())
                vehicle_choice = int(input(f"Select vehicle type (1-{len(vehicle_keys)}): ")) - 1
                
                if 0 <= vehicle_choice < len(vehicle_keys):
                    selected_vehicle = vehicle_keys[vehicle_choice]
                    self.resize_silhouette(selected_file, selected_vehicle)
                else:
                    print("Invalid vehicle selection")
            else:
                print("Invalid file selection")
                
        except (ValueError, IndexError):
            print("Invalid input")

def main():
    """Main execution function"""
    resizer = KenRulebookResizer()
    
    print("=" * 60)
    print("KEN'S RULEBOOK SILHOUETTE RESIZER")
    print("=" * 60)
    print("Apply Maus-based proportional scaling to existing silhouettes")
    print(f"Input folder: {resizer.input_dir}")
    print(f"Output folder: {resizer.output_dir}")
    print()
    
    print("Options:")
    print("1. Auto-detect and resize all silhouettes")
    print("2. Manually select specific files")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ")
    
    if choice == "1":
        resizer.auto_detect_and_resize()
    elif choice == "2":
        resizer.resize_specific_files()
    else:
        print("Exiting...")
        return
    
    print(f"\n🎯 Next steps:")
    print(f"1. Check output in: {resizer.output_dir}")
    print(f"2. Use resized silhouettes for counter creation")
    print(f"3. Test print at 0.5\" scale")

if __name__ == "__main__":
    main()