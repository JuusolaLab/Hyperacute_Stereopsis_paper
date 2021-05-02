#in this library, there are all the functions used for static plotting
import numpy as np
import plotly.graph_objs as go

def corr_heatmap(corr,names):
	trace = go.Heatmap(
		z=corr,
		x=names,
		y=names,
		colorbar = dict(
			len = .3,
			y = 1,
			yanchor = "top"
		)
	)
	return trace

def plotline(x,y,xaxis,yaxis,name,width = 2, color = 'black',legendgroup=None,showlegend=True):
	if legendgroup is not None:
		trace = go.Scatter(
			x=x,
			y=y,
			xaxis = xaxis,
			yaxis = yaxis, 
			name = name,
			legendgroup = legendgroup,
			showlegend = showlegend,
			line = dict(color = color, width = width)
		)
	else:
		trace = go.Scatter(
			x=x,
			y=y,
			xaxis = xaxis,
			yaxis = yaxis, 
			name = name,
			showlegend = showlegend,
			line = dict(color = color, width = width)
		)
	return trace
	
def plotbar(t,min,max,name = '',showlegend = False,color = 'black',legendgroup="group",text = '',hovertext = '',mode='lines',width = 1,stim_angle = 0):
	if stim_angle == 90:
		return (
		go.Scatter(
			x = [min,max],
			y= [t,t],
			name= name,
			legendgroup=legendgroup,
			showlegend = showlegend,
			text = text,
			hovertext =hovertext,
			mode=mode,
			line= dict(color=color,width=width)
		)
	)
	else:
		return (
			go.Scatter(
				x = [t,t],
				y= [min,max],
				name= name,
				legendgroup=legendgroup,
				showlegend = showlegend,
				text = text,
				hovertext =hovertext,
				mode=mode,
				line= dict(color=color,width=width)
			)
		)
def plottable(data):
	print('keys: ', list(data.keys()))
	print('values: ', [data[k] for k in data.keys()])
	return (
		go.Table(header=dict(values=list(data.keys())),
                 cells=dict(values=[data[k] for k in data.keys()]))
	)

def plotpoints(x,y,xaxis,yaxis,name,width=2,showlegend = False,color = 'black'):
	return(
		go.Scatter(
		x=x,
		y=y,
		xaxis = xaxis,
		yaxis = yaxis,
		name = name,
		mode = 'markers',
		marker = dict(color=color,size=width),
		showlegend = showlegend
		)
	)

def plotrect(x0,x1,y0,y1,color,name,showlegend = True,transparency = .6):
	 return(
		go.Scatter(
		x=[x0,x0,x1,x1,x0],
		y=[y0,y1,y1,y0,y0],
		fill="toself",
		fillcolor='rgba'+str(color)[0:-1]+','+str(transparency)+')',
			line=dict(
				color="black",
				width=2
			),
		name = name,
		showlegend = showlegend
		)
	)
	
def addtext(dic,xref,yref):
	keys = list(dic.keys())
	values = list(dic.values())
	toadd = [dict(
				x= 1,
				y=k+1,
				xref = xref,
				yref = yref,
				axref = xref,
				ayref = yref,
				text=keys[k]+': '+str(values[k]),
				showarrow=False
			)for k in range(0, len(dic))]
	return toadd
	
def addarrows(x,y,dx,dy,xref,yref):
	toadd = [dict(
				x=x[k]+ dx[k],
				y=y[k]+ dy[k],
				xref = xref,
				yref = yref,
				axref = xref,
				ayref = yref,
				text='',
				showarrow=True,
				arrowhead=2,
				ax=x[k],
				ay=y[k],
				arrowcolor='black'
			)for k in range(0, len(x), 1)]
	return toadd