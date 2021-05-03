using PyCall, Images, Infiltrator, JLD, Makie, DelimitedFiles, GeometryBasics, GeometryTypes#GeometryBasics #ColorCoding
io = pyimport("skimage.io")

const test_im = raw"C:\Users\James\OneDrive\Sheffield\Python\Read Images\Better Data\test_im.tif"
const infolder = raw"C:\Users\James\Documents\Data\Gal4 Expression Data\Best Tiffs"
const outfolder = raw"C:\Users\James\OneDrive\Sheffield\Python\Read Images\Better Data"


"""
Reading and Loading
"""
read_image(fname) = io.imread(fname)

load_indices(fname) = load(fname,"indices")

function read_normalised(fname)
	stack = read_image(fname)
	normed = normalise(stack[:,:,:,1:3])
	return normed
end

function read_background(fname)
	stack = read_image(fname)
	normalise(stack[:,:,:,4])
end

function plot_all(folder)

	files = searchdir(folder, ".jld")
	s = plot_all(folder, files)
end

function plot_all(folder, files::Array{String,1})

	colors = range(HSLA(0,0.8,0.6, 1.0), HSLA(360,0.8,0.6, 1.0), length=length(files))
	ids = unique_id.(files)
	s = nothing
	for (i,f) in enumerate(files)
		indices = load_indices(folder * "\\" * f)
		s = plot_indices!(s, indices, color=colors[i])
	end
	return s
end

function plot_all!(scene, folder)
	files = searchdir(folder, ".jld")
	scene = plot_all!(scene, folder, files);
	return scene
end

function plot_all!(scene, folder, files::Array{String, 1})
	colors = range(HSLA(0,1.,.6, 1.), HSLA(360,1.,.6, 1.), length=length(files))
	ids = unique_id.(files)
	for (i,f) in enumerate(files)
		indices = load_indices(folder * "\\" * f)
		scene = plot_indices!(scene, indices, color=colors[i])
	end
	return scene
end

function volume_plot_indices!(scene, folder, files::Array{String, 1})
	colors = range(HSLA(0,0.8,0.6, 1.0), HSLA(360,0.8,0.6, 1.0), length=length(files))
	ids = unique_id.(files)

	arena_size = (174, 566, 1210)

	for (i,f) in enumerate(files)
		indices = load_indices(folder * "\\" * f)
		image = points_to_array(indices, arena_size)
		scene = volume!(scene, image, algorithm=:iso, isorange=0.04, isovalue=1)
	end
	return scene
end

"""
pipeline
"""
function pipeline(fname::String)

	stack = read_image(infolder * "\\" * fname)
	not_chosen = true
	while not_chosen
		
		threshold = ask_for_threshold()
		threshed = threshold_image(get_channel(stack,1:3), threshold, 1.0)
		red_points = positive_indices(get_channel(threshed,1))
		green_points = positive_indices(get_channel(threshed,2))
		blue_points = positive_indices(get_channel(threshed,3))
		color_indices = (red_points, green_points, blue_points)

		channel = view_channel(color_indices)
		not_chosen = save_channel(color_indices[channel], fname)
	end
end

function save_channel(color_indices, fname)

	println("Save Channel? (Y/N)")
	save_this = readline() in ["Y", "y"]

	save_this && save_file(fname, color_indices)

	open(outfolder * "\\files_analysed.txt", "a") do io
		writedlm(io, fname)
	end

	return !save_this
end

function save_file(fname, indices)

	newname = outfolder * "\\" * fname * ".jld"
	!isfile(newname) ? save(newname, "indices", indices) : save_file(fname * "(2)", indices)
end

function ask_for_threshold()
	println("threshold?")
	return UInt16(parse(Int, readline()))
end

function view_channel(indices)

	still_looking = true
	channel = 1

	while still_looking
		println("Which Channel?")
		channel = parse(Int64, readline())
		s = plot_indices(indices[channel])
		display(s)
		println("New Channel?")
		still_looking = readline() in ["Y", "y"]
	end

	return channel
end


"""
plotters
"""
function plot_indices(indices; color=:black)

	s = scatter(indices, markersize=1, color=color, strokewidth=0)
	cameracontrols(s).rotationspeed[] = 0.002f0
	return s
end

function plot_indices!(s::Nothing, indices; color=:black)
	
	s = Scene(resolution=(3840/2, 2160/2))
	Makie.scatter!(s, indices, markersize=1.1, color=color, show_axis=false, transparency=true, scale_plot=false, marker='■')
	cameracontrols(s).rotationspeed[] = 0.002f0
	return s
end

function plot_indices!(s::Scene, indices; color=:black)
	scatter!(s, indices, color=color, markersize=2., transparency=true, show_axis=false, scale_plot=false, marker='■')
	return s
end

function spinning_camera(s, time_seconds)
	s.center = false
	spinning_time = [1:time_seconds;]
	rotate_cam!(scene, (0.0,0.0,0.0))	
	for _ in spinning_time		
		rotate_cam!(s, (0.0, 0.0, 0.01))
		sleep(0.01)
	end
end

function save_spinning_camera(s, rotations, fname)
	s.center = false
	frames = 300
	rotate_cam!(s, (0.0,0.0,0.0))

	record(s, outfolder * "\\" * fname, 1:frames; framerate=30) do i
       rotate_cam!(s, 0., (2π)/300, 0.)
       #update_cam!(s) # disabling stops the camera reset.
   end

end


"""
Data Manipulation
"""

threshold_image(image, threshold, above_value) = (image .> threshold) .* above_value

get_channel(slice::Array{<:Any, 3}, channel) = slice[:,:,channel]
get_channel(stack::Array{<:Any, 4}, channel) = stack[:,:,:,channel]

get_slice(stack::Array{<:Any,3}, slice) = stack[slice,:,:]
get_slice(stack::Array{<:Any,4}, slice) = stack[slice,:,:,:]

function convert_to_image(stack; type=HSL)

	return type.(colorview(RGB, get_channel(stack, 1), get_channel(stack,2), get_channel(stack,3) ))
end

function positive_indices(a)

	i_max, j_max, k_max = size(a)
	indices = Point{3,Int}[]
	for i in 1:i_max, j in 1:j_max, k in 1:k_max

		a[i,j,k] > zero(eltype(a)) && push!(indices, Point(i,j,k))
	end
	return indices
end

function segregate_hues(image_stack)

	hues = get_hues(image_stack)
	unique_hues = unique(hues)
	# we don't want to find the black space so delete this.
	deleteat!(unique_hues, findfirst(x -> x==0.0, unique_hues))

	pixel_positions = Array{CartesianIndex{3},1}[]

	for h in unique_hues 
		
		push!(pixel_positions,findall(x -> x==h, hues))
	end
	return pixel_positions
end


"""
Tools
"""

cartesian_to_point(cart::Array{CartesianIndex{3},1}) = cartesian_to_point.(cart)
cartesian_to_point(cart::CartesianIndex{3}) = Point(cart[1], cart[2], cart[3])
cartesian_to_point(cart::CartesianIndex{2}) = Point(cart[1], cart[2])
cartesian_to_point(cart::CartesianIndex{1}) = Point(cart[1])

@inline normalise(stack::Array{<:Real, 3}) = (stack .- minimum(stack)) ./ (maximum(stack) - minimum(stack))
function normalise(stack::Array{<:Any, 4})

	normed = Array{Float64, 4}(undef, size(stack)...)

	for i in 1:size(stack)[4]

		 normed[:,:,:,i] .= normalise(stack[:,:,:,i])
	end
	return normed
end

searchdir(path,key) = filter(x->occursin(key,x), readdir(path))

unique_id(s) = s[1:21]
gal4(s) = s[1:6]
bodyid(s) = s[8:15]

function points_to_array(points, array_size)

	arena = zeros(Int, array_size)

	for point in points

		setindex!(arena, 1, point[1], point[2], point[3])
	end
	return arena
end