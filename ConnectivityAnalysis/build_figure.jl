include(raw"C:\Users\James\OneDrive\Sheffield\Python\Read Images\julia_stuff.jl");
include(raw"C:\Users\James\OneDrive\Sheffield\Julia\canny_edge\plot_background.jl");
include(raw"C:\Users\James\OneDrive\Sheffield\Julia\canny_edge\sobel.jl");


files =  ["R12F03-20181121_64_F4-f-40x-central-GAL4-JRC2018_Unisex_20x_HR-8213901-aligned_stack.tif.jld",
 "VT047848-20171020_66_I1-f-40x-Brain-GAL4-JRC2018_Unisex_20x_HR-8235457-aligned_stack.tif(2).jld",
 "VT047848-20171020_66_I1-f-40x-Brain-GAL4-JRC2018_Unisex_20x_HR-8235457-aligned_stack.tif.jld",
 "VT047848-20171020_66_I2-f-40x-Brain-GAL4-JRC2018_Unisex_20x_HR-8235463-aligned_stack.tif.jld",
 "VT047848-20171020_66_I5-f-40x-Brain-GAL4-JRC2018_Unisex_20x_HR-8235439-aligned_stack.tif.jld",
 "VT047848-20171020_66_J1-f-40x-Brain-GAL4-JRC2018_Unisex_20x_HR-8235445-aligned_stack.tif.jld",
 "VT062633-20170929_61_D3-f-40x-Brain-GAL4-JRC2018_Unisex_20x_HR-8215118-aligned_stack.tif.jld",
 "VT062633-20170929_61_D6-f-40x-Brain-GAL4-JRC2018_Unisex_20x_HR-8215132-aligned_stack.tif.jld"]

scene = Scene(show_axis=false);
plot_background!(scene, test_im);
plot_all!(scene, raw"C:\Users\James\OneDrive\Sheffield\Python\Read Images\Better Data", files);
cameracontrols(scene).rotationspeed[] = 0.02f0;

scene
