from ansys.fluent.core import launch_fluent
from pathlib import Path
import time

def create_static_mixer_mesh(geometry_path, output_path):
   
    # Convert to Path objects and validate
    geom_path = Path(geometry_path).resolve()
    out_path = Path(output_path).resolve()
    
    # Validate input file path
    if not geom_path.exists():
        raise FileNotFoundError(f"Geometry file not found at:\n{geom_path}")
    
    # Ensure output directory exists
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Using geometry file: {geom_path}")
    print(f"Output will be saved to: {out_path}")
    
    # Launch Fluent with GUI enabled
    print("Launching Fluent with GUI...")
    meshing = launch_fluent(
        mode="meshing",
        precision="double",
        show_gui=True,
        processor_count=2,
        start_timeout=120
    )
    
    try:
        # Get workflow controller
        workflow = meshing.workflow
        
        # Print all available tasks before initialization
        print("\nAvailable tasks before initialization:")
        for task in workflow.TaskObject:
            print(f"  - {task}")
        
        # Initialize workflow
        print("\nInitializing workflow...")
        workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
        
        # Import geometry using workflow
        print("Importing geometry...")
        workflow.TaskObject["Import Geometry"].Arguments = {
            "FileName": str(geom_path),
            "LengthUnit": "m"
        }
        workflow.TaskObject["Import Geometry"].Execute()
        
        # Print all available tasks after geometry import
        print("\nAvailable tasks after geometry import:")
        for task in workflow.TaskObject:
            print(f"  - {task}")
            
        # Wait for user to verify tasks and check correct task names
        print("\nPlease check the task names in the Fluent GUI.")
        print("Look for the exact name of the mesh saving task.")
        input("Press Enter once you've noted the correct task name...")
        
        # Generate surface mesh using the correct task name
        print("\nGenerating surface mesh...")
        surface_mesh_task = "Generate the Surface Mesh"
        workflow.TaskObject[surface_mesh_task].Execute()
        
        # Generate volume mesh
        print("Generating volume mesh...")
        volume_mesh_task = "Generate the Volume Mesh"
        workflow.TaskObject[volume_mesh_task].Execute()
        
        # Try different common task names for saving mesh
        save_tasks = [
            "Save Mesh",
            "Write Output",
            "Export Mesh",
            "Write Mesh",
            "Save Output"
        ]
        
        mesh_saved = False
        for task_name in save_tasks:
            try:
                if task_name in workflow.TaskObject:
                    print(f"\nTrying to save mesh using task: {task_name}")
                    workflow.TaskObject[task_name].Arguments = {
                        "FileName": str(out_path),
                        "FileType": "Case"
                    }
                    workflow.TaskObject[task_name].Execute()
                    mesh_saved = True
                    print(f"Successfully saved mesh using {task_name}")
                    break
            except Exception as e:
                print(f"Could not save using {task_name}: {str(e)}")
                continue
        
        if not mesh_saved:
            print("\nCould not automatically save the mesh.")
            print("Available tasks are:")
            for task in workflow.TaskObject:
                print(f"  - {task}")
            print("\nPlease note the correct task name from above and update the code.")
        
        return meshing
        
    except LookupError as e:
        print(f"\nTask name error: {str(e)}")
        print("\nAvailable tasks are:")
        for task in workflow.TaskObject:
            print(f"  - {task}")
        meshing.exit()
        raise
    except Exception as e:
        print(f"Error during meshing: {str(e)}")
        meshing.exit()
        raise

def main():
    # Define paths
    INPUT_DIR = Path("C:/Users/RAFA/Desktop/Schule/UANL/9no/Servicio/ANSYS/Pyfluent/curso/PyF_L3_WF/Workshop_files/Input_files").resolve()
    OUTPUT_DIR = Path("C:/Users/RAFA/Desktop/Schule/UANL/9no/Servicio/ANSYS/Pyfluent/curso/PyF_L3_WF/Workshop_files/Output_files").resolve()
    
    # Print available files in input directory
    print("Available files in input directory:")
    for file in INPUT_DIR.glob("*.*"):
        print(f"  - {file.name}")
    
    GEOMETRY_FILE = INPUT_DIR / "Static Mixer geometry.pmdb"
    OUTPUT_FILE = OUTPUT_DIR / "static_mixer_mesh.msh"
    
    try:
        start_time = time.time()
        print("Starting meshing process...")
        
        meshing_session = create_static_mixer_mesh(GEOMETRY_FILE, OUTPUT_FILE)
        
        end_time = time.time()
        print(f"Total meshing time: {end_time - start_time:.2f} seconds")
        
        input("Press Enter to close Fluent...")
        
    finally:
        if 'meshing_session' in locals():
            meshing_session.exit()

if __name__ == "__main__":
    main()