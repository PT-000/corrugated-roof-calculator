import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set page configuration
st.set_page_config(
    page_title="Corrugated Roof Calculator",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def calculate_corrugated_profile(A, D, degree, total_length):
    """Calculate the actual corrugated profile with realistic geometry"""
    # Convert angle to radians
    radian = np.deg2rad(degree)
    
    # Calculate the horizontal distance from valley to peak
    L = round(D / np.tan(radian), 2)
    
    # Calculate actual slant length (hypotenuse)
    slant_length = round(D / np.sin(radian), 2)
    
    # One complete corrugation cycle consists of:
    # - Flat bottom (A)
    # - Slant up (slant_length)
    # - Slant down (slant_length)
    module_physical_length = A + 2 * slant_length
    
    # Calculate how many complete modules we can fit
    N = int(total_length // module_physical_length)
    
    # Calculate used length and leftover
    used_length = N * module_physical_length
    leftover = total_length - used_length
    
    # Generate the actual corrugated profile
    x_profile = []  # Horizontal position
    z_profile = []  # Vertical position (height)
    
    x_current = 0
    
    for i in range(N):
        # Flat bottom section
        x_profile.extend([x_current, x_current + A])
        z_profile.extend([0, 0])
        x_current += A
        
        # Slant up to peak
        x_profile.append(x_current + L)
        z_profile.append(D)
        x_current += L
        
        # Slant down to valley
        x_profile.append(x_current + L)
        z_profile.append(0)
        x_current += L
    
    # Always end with a flat segment of length A
    if N > 0:  # Only if we have at least one complete module
        x_profile.extend([x_current, x_current + A])
        z_profile.extend([0, 0])
        x_current += A
        # Adjust used length to include the final flat segment
        used_length += A
        leftover = total_length - used_length
    
    # Handle leftover material
    leftover_profile_x = []
    leftover_profile_z = []
    
    if leftover > 0:
        if leftover >= slant_length:
            # Add complete slant up
            leftover_profile_x.append(x_current + L)
            leftover_profile_z.append(D)
            x_current += L
            leftover -= slant_length
            
            # Add partial slant down if remaining
            if leftover > 0:
                partial_slant = min(leftover, slant_length)
                partial_height = D - (partial_slant * np.sin(radian))
                partial_horizontal = partial_slant * np.cos(radian)
                
                leftover_profile_x.append(x_current + partial_horizontal)
                leftover_profile_z.append(max(0, partial_height))
        else:
            # Partial slant up only
            partial_slant = leftover
            partial_height = partial_slant * np.sin(radian)
            partial_horizontal = partial_slant * np.cos(radian)
            
            leftover_profile_x.append(x_current + partial_horizontal)
            leftover_profile_z.append(partial_height)
    
    return (x_profile, z_profile, leftover_profile_x, leftover_profile_z, 
            N, module_physical_length, L, slant_length, used_length, leftover)

def create_main_plot(x_profile, z_profile, leftover_x, leftover_z, A, D, N, efficiency, design_failed):
    """Create the main corrugated profile plot"""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Set background color based on failure status
    if design_failed:
        ax.set_facecolor('#ffeeee')
    else:
        ax.set_facecolor('white')
    
    if x_profile and z_profile:
        # Choose colors based on failure status
        main_color = 'red' if design_failed else 'blue'
        leftover_color = 'darkred' if design_failed else 'red'
        
        # Plot main corrugated profile
        ax.plot(x_profile, z_profile, color=main_color, linewidth=2, 
                marker='o', markersize=3, label='Corrugated Profile')
        
        # Plot leftover material
        if leftover_x and leftover_z:
            leftover_label = f'Leftover - Partial'
            ax.plot(leftover_x, leftover_z, color=leftover_color, linewidth=3, 
                    marker='s', markersize=4, label=leftover_label)
            # Fill under the curve
            ax.fill_between(leftover_x, leftover_z, alpha=0.3, color=leftover_color)
        
        # Fill under main profile
        ax.fill_between(x_profile, z_profile, alpha=0.2, color=main_color)
    
    # Set plot properties
    title_color = 'red' if design_failed else 'black'
    ax.set_title(f'Corrugated Roof Profile - {N} Complete Modules (Efficiency: {efficiency:.1f}%)', 
                color=title_color, fontweight='bold', fontsize=14)
    ax.set_xlabel('Length (mm)')
    ax.set_ylabel('Height (mm)')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Dynamic limits
    if x_profile:
        max_x = max(x_profile + leftover_x) if leftover_x else max(x_profile)
        ax.set_xlim(0, max_x * 1.05)
        ax.set_ylim(-D*0.1, D*1.2)
    
    return fig

def create_cross_section_plot(A, D, L, degree):
    """Create the cross-section plot"""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Draw one complete corrugation cross-section
    x_cross = [0, A, A + L, A + 2*L, A + 2*L + A]
    z_cross = [0, 0, D, 0, 0]
    
    ax.fill(x_cross, z_cross, alpha=0.2, color='lightblue', label='Cross-section')
    ax.plot(x_cross, z_cross, 'b-', linewidth=3)
    
    # Dimensions
    # Flat bottom dimension (A)
    ax.annotate('', xy=(0, -D*0.18), xytext=(A, -D*0.18),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax.text(A/2, -D*0.28, f'A = {A}mm', ha='center', color='red', 
            fontweight='bold', fontsize=10)
    
    # Height dimension (D)
    ax.annotate('', xy=(A + L - 10, 0), xytext=(A + L - 10, D),
                arrowprops=dict(arrowstyle='<->', color='green', lw=2))
    ax.text(A + L - 25, D/2, f'D = {D}mm', ha='center', color='green', 
            fontweight='bold', fontsize=10, rotation=90)
    
    ax.set_title('Cross-Section View (One Module)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Width (mm)')
    ax.set_ylabel('Height (mm)')
    ax.grid(True, alpha=0.2)
    ax.set_aspect('equal')
    
    # Set limits
    peak_to_peak = A + 2*L
    ax.set_xlim(-peak_to_peak*0.15, peak_to_peak*1.15)
    ax.set_ylim(-D*0.4, D*1.5)
    
    return fig

# Main Streamlit App
def main():
    st.title("🏠 Corrugated Roof Calculator")
    st.markdown("Calculate corrugated roofing profiles with material optimization")
    
    # Sidebar controls
    st.sidebar.header("Design Parameters")
    
    A = st.sidebar.slider(
        "Flat Bottom Width (A) - mm", 
        min_value=10, max_value=200, value=50, step=1,
        help="Width of the flat bottom section"
    )
    
    D = st.sidebar.slider(
        "Peak Height (D) - mm", 
        min_value=10, max_value=200, value=60, step=1,
        help="Height of the corrugation peak"
    )
    
    degree = st.sidebar.slider(
        "Fold Angle - degrees", 
        min_value=15, max_value=85, value=45, step=1,
        help="Angle of the corrugation sides"
    )
    
    total_length = st.sidebar.slider(
        "Total Sheet Length - mm", 
        min_value=1000, max_value=5000, value=2440, step=10,
        help="Available sheet material length"
    )
    
    # Calculate profile
    (x_profile, z_profile, leftover_x, leftover_z, N, module_length, 
     L, slant_length, used_length, leftover) = calculate_corrugated_profile(
        A, D, degree, total_length)
    
    # Check if design failed
    design_failed = used_length > total_length
    efficiency = (used_length / total_length) * 100 if total_length > 0 else 0
    
    # Calculate additional parameters
    peak_to_peak = A + 2*L
    total_flat_length = (N + 1) * A
    total_slant_length = N * 2 * slant_length
    coverage_width = N * peak_to_peak
    
    # Display failure warning if needed
    if design_failed:
        st.error("⚠️ Design Failure: Required material exceeds available sheet length!")
    
    # Main plots
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Corrugated Profile")
        main_fig = create_main_plot(x_profile, z_profile, leftover_x, leftover_z, 
                                   A, D, N, efficiency, design_failed)
        st.pyplot(main_fig, use_container_width=True)
    
    with col2:
        st.subheader("Cross-Section")
        cross_fig = create_cross_section_plot(A, D, L, degree)
        st.pyplot(cross_fig, use_container_width=True)
    
    # Specifications in two columns
    st.subheader("Specifications")
    spec_col1, spec_col2 = st.columns(2)
    
    with spec_col1:
        # Determine styling based on failure
        if design_failed:
            st.markdown("""
            <div style="background-color: #ffcccc; padding: 15px; border-radius: 10px; border: 2px solid red;">
            <h4 style="color: darkred;">Basic Specifications</h4>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color: white; padding: 15px; border-radius: 10px; border: 2px solid darkblue;">
            <h4 style="color: darkblue;">Basic Specifications</h4>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        **BASIC PARAMETERS:**
        - Flat Bottom Width (A): {A} mm
        - Peak Height (D): {D} mm
        - Fold Angle: {degree}°
        - Total Sheet Length: {total_length} mm
        
        **CALCULATED DIMENSIONS:**
        - Slant Length: {slant_length:.1f} mm
        - Peak-to-Peak Distance: {peak_to_peak:.1f} mm
        - Module Length: {module_length:.1f} mm
        
        **ROOF CONFIGURATION:**
        - Complete Modules: {N}
        - Coverage Width: {coverage_width:.1f} mm
        - Material Efficiency: {efficiency:.1f}%
        - Leftover Material: {leftover:.1f} mm
        """)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with spec_col2:
        if design_failed:
            st.markdown("""
            <div style="background-color: #ffcccc; padding: 15px; border-radius: 10px; border: 2px solid red;">
            <h4 style="color: darkred;">Material & Structural Analysis</h4>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color: white; padding: 15px; border-radius: 10px; border: 2px solid darkblue;">
            <h4 style="color: darkblue;">Material & Structural Analysis</h4>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        **MATERIAL BREAKDOWN:**
        - Flat Sections Total: {total_flat_length} mm
        - Slant Sections Total: {total_slant_length:.0f} mm
        - Used Material: {used_length:.1f} mm
        - Available Material: {total_length} mm
        
        **STRUCTURAL PROPERTIES:**
        - Surface Area Increase: {(module_length/peak_to_peak):.2f}x
        - Corrugation Ratio: {(D/peak_to_peak):.3f}
        - Bending Strength Factor: {(D**2/peak_to_peak):.1f}
        
        **MANUFACTURING NOTES:**
        - Bend Radius: {(A/4):.1f} mm (recommended)
        - Tooling Angle: {degree}° ± 2°
        - Material Utilization: {((total_length-leftover)/total_length*100):.1f}%
        """)
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
