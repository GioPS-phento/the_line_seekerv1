# the_line_seekerv1
A little pandas based project to find the optimal route of a F1 car in a session, where the kinetic energy is maximun
the graphic shows the best trayectories of Sergio "Checo" Perez in Silverstone 2022
<img width="390" height="253" alt="checobesttrayectori" src="https://github.com/user-attachments/assets/cec598cc-aa63-4582-a052-25256b4392c8" />

The problem to solve was that the pilots presumably (in the point of view of a mortal gamer)cannot know how the trayectory affects the kinematic energy  or even their race engineers, so I decided to gater the data of a real race and make some manipulations to obtain the trayectories whit the highest kinematic energy mean.

The program works by fetching the data of a determined driver in a certain Race using the fastf1 package. Then, a for loop is used to make a custom dataset with the fields we need to get the work done.
   
    all_telemetry.append(tel[['LapNumber', 'Energia_cinetica_J','Distance','X','Y']])  

Next, the information of the circuit is obtained, and with the use of a lambda and a short function, the corners of the circuit get a tag.
       
       circuit_info = session.get_circuit_info()
       corners = circuit_info.corners
Then the data is cleaned using quantile features to delete outliers, like pit stops, yellow flags, red flags.

Finally, the data is arranged by curve into a dictionary, putting the curve name with its respective dataset.
        
        for curva in curvas:
        
            dtcur[curva] = full_telemetry[full_telemetry['Curva'] == curva]
Then the kinematic energy is obtained from the dictionary and grouped by mean. In the next step, the address of the max mean from the data is stored in a vector, lapnum, this will help later to locate the data.

        for nombre, dtf in dtcur.items():
            newdtf=dtf.groupby('LapNumber')['Energia_cinetica_J'].mean().reset_index()
            lapnum.append(newdtf['Energia_cinetica_J'].idxmax())
At last, using zip(), the specific data grouped by curve and lap with the highest energy mean is extracted into another dictionary, then the data from the dictionary is plotted.

        for cruva ,lap in zip(curvas,lapnum):
                trayectoria[cruva]=full_telemetry[(full_telemetry['Curva'] == cruva) & (full_telemetry['LapNumber'] == lap)]
And draw the optimal route into the track map 

