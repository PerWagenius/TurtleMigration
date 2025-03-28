import Agent as agent
import numpy as np
import pickle
import MagneticModel as magmod
import AxesmMagneticMap as axesmap
# Example Usage
#magmodel=magmod.MagneticModel(1.0)
#with open('magmodel.pkl', 'wb') as file:
#    pickle.dump(magmodel, file)
with open('magmodel.pkl', 'rb') as file:
    magmodel = pickle.load(file)
map = axesmap.AxesmMagneticMap(magmodel)
map.initialize_axes()
#Slat,Slon=-5.2367, -35.4049  # Brazil coast
#Glat,Glon=-7.923, -14.407  # Ascension Island
Slat,Slon=-21.115141, 55.536384 # Example coordinates for Reunion
Glat, Glon=17.7,56.3 # Example coordinates for Oman
Turtle=agent.Agent(magmodel,verbose=False)
Turtle.SetAMatrix(np.array([[1, 0], [0, 1]])) #stable node
#Turtle.SetAMatrix(np.array([[-10, -10], [2, 0]])/10) #stability spiral source
#Turtle.SetAMatrix(np.array([[8, -4], [1, 0]])/10) # Spiral sink (medium green)
#Turtle.SetAMatrix(np.array([[7, 0], [8, 0]])/10) # Neutrally stable
#Turtle.SetAMatrix(np.array([[-10, -10], [2, 3]])/10) #Unstable
Turtle.SetStart(Slat,Slon)
Turtle.SetGoal(Glat,Glon)
Turtle.Reset()
#Turtle.Step(50000)
Turtle.Run()
Lats,Longs=Turtle.GetTraj()
map.update_agent_start(Slat,Slon)  
map.update_agent_goal(Glat,Glon)  
map.update_agent_trajectory(Lats,Longs)
map.draw_stability_mesh(Turtle.A)
map.show()

#map.update_agent_start(-21.115141, 55.536384)  # Example coordinates for Reunion
#map.update_agent_goal(21.512583, 55.923255)  # Example coordinates for Oman
#map.update_agent_trajectory([34.05, 36.16, 40.71], [-118.25, -115.15, -74.01])
