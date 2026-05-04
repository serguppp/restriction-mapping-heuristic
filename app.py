import streamlit as st
import subprocess
import json
import time

# Page settings
st.set_page_config(page_title="Restriction Mapping Heuristics", layout="centered")
st.title("Restriction Mapping Heuristics")

# UI
st.sidebar.header("Input Parameters")
m = st.sidebar.slider("P size", min_value=5, max_value=100, value=10)
max_val = st.sidebar.number_input("Max Distance Value", min_value=10, max_value=1000, value=100)

if st.button("Generate P and D", type="primary", use_container_width=True):
    
    with st.spinner(f"Generating P and D for m={m}..."):
        start_time = time.time()
        
        try:
            process = subprocess.run(
                ["./src/main", str(m), str(max_val)], 
                capture_output=True, 
                text=True, 
                check=True
            )
            elapsed_time = time.time() - start_time
            
            result_json = json.loads(process.stdout)
            
            if result_json.get("status") == "success":
                st.success(f"Calculations completed in {elapsed_time:.4f} seconds!")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Generated Points P")
                    st.write(result_json["p_points"])
                    
                with col2:
                    st.subheader("Set of Distances D")
                    distances = result_json["d_distances"]
                    st.write(distances[:20] if len(distances) > 20 else distances)
                    if len(distances) > 20:
                        st.caption(f"... {len(distances) - 20} and more.")
                
            else:
                st.error("C++ returned a logical error:")
                st.write(result_json.get("message"))

        except subprocess.CalledProcessError as e:
            st.error("C++ compiler error")
            st.code(e.stderr)
        except FileNotFoundError:
            st.error("C++ executable not found.")
        except json.JSONDecodeError:
            st.error("JSON parsing error.")
            st.code(process.stdout)