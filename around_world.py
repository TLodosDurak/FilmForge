import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import imageio.v2 as imageio
import numpy as np
import random
import math
from scripts.utils import find_nearest_country
from moviepy.editor import ImageSequenceClip
import time


# Global counter for frame
frame_counter = 0

def oscillate_color(color, amplitude, frequency, phase_shift=0):
    global frame_counter
    color = color.lstrip('#')
    r, g, b = int(color[:2], 16), int(color[2:4], 16), int(color[4:], 16)

    # Oscillate the color values using sine function
    r = max(0, amplitude * np.sin(2.0 * np.pi * frequency * frame_counter + phase_shift) + r)
    g = max(0, amplitude * np.sin(2.0 * np.pi * frequency * frame_counter + np.pi/2 + phase_shift) + g)
    b = max(0, amplitude * np.sin(2.0 * np.pi * frequency * frame_counter + np.pi + phase_shift) + b)

    # Clamping values between 0 and 255
    r = min(255, max(0, r))
    g = min(255, max(0, g))
    b = min(255, max(0, b))

    new_color = '#{:02x}{:02x}{:02x}'.format(int(r), int(g), int(b))

    return new_color
    
def generate_map(ranking_list, title_duration, frame_duration, outro_duration, thread_id, highlight_colors_sampled):
    start_time = time.time()
    global frame_counter
    # Load a GeoDataFrame with country shapes
    world = gpd.read_file(
        'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\src\\files\\ne_50m_admin_0_countries.shp')

    # Define colors for land, water and highlighted country
    land_color = '#bdb67e'
    water_color = '#74b3c4'
    # land_color = '#636061'
    # water_color = '#000000'
    current_country_color = '#db1620'
    past_country_color = '#800e14'
    # for i in range(random.randint(1, 20)):
    #     water_color = oscillate_color(water_color, amplitude=100, frequency=0.05)

    # Randomly sample 10 colors for highlighting countries
    #highlight_colors_sampled = random.sample(highlight_colors, 10)

    # Your top 10 countries list
    country_list = ranking_list

    countries = world['ADMIN'].unique().tolist()

    # Replace your existing country names in country_list with the nearest match from the geopandas dataframe
    country_list = [find_nearest_country(country, countries) for country in country_list]

    images = []

    fps = 24  # frames per second

    # Initial frame bounds
    xmin_frame, xmax_frame, ymin_frame, ymax_frame = -180, 180, -90, 90

    # Total frames calculation
    total_frames = (title_duration * fps) + (len(country_list) * frame_duration * fps) + (outro_duration * fps)


    # Initialize a dictionary to store the countries and their corresponding colors
    countries_to_highlight = {}

    for frame in range(math.ceil(title_duration * fps)):
        fig, ax = plt.subplots(1, 1)
         # Oscillate the color for each frame
        #water_color = oscillate_color(water_color, amplitude=10, frequency=0.01)
        fig.set_facecolor(water_color)
        world.plot(color=land_color, edgecolor='black', ax=ax)
        ax.axis('off')
        ax.set_aspect('equal')

        # zoom target
        target_xmin = -120
        target_xmax = 120
        target_ymin = -45
        target_ymax = 75
        # zoom increments
        dxmin, dymin, dxmax, dymax = (target_xmin - xmin_frame) / (1.5*fps), (target_ymin - ymin_frame) / (
            1.5*fps), (target_xmax - xmax_frame) / (1.5*fps), (target_ymax - ymax_frame) / (1.5*fps)
        xmin_frame += dxmin
        xmax_frame += dxmax
        ymin_frame += dymin
        ymax_frame += dymax
        # Apply zoom effects
        ax.set_xlim(xmin_frame, xmax_frame)
        ax.set_ylim(ymin_frame, ymax_frame)

        # Save each figure to a file
        fig.savefig(
            f'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\maps\\map{frame}_{thread_id}.png', dpi=200)
        plt.close(fig)
        images.append(imageio.imread(
            f'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\maps\\map{frame}_{thread_id}.png'))
        # Progress update
        if (frame+1) % 10 < 1:
            elapsed_time = time.time() - start_time
            minutes, seconds = divmod(elapsed_time, 60)
            # Calculate the estimated minutes and seconds
            estimated_minutes, estimated_seconds = divmod(total_frames - (frame+1), 60)
            print(f'Frame {frame+1}/{total_frames} ({100*(frame+1)/total_frames:.2f}%) generated. Estimated time: {int(estimated_minutes)} mins {int(estimated_seconds)} secs, Elapsed time: {int(minutes)} mins {int(seconds)} secs')
        frame_counter += 1


    # Keep track of visited countries and their colors
    visited_countries = {}
    buffer_percentage = 2
    for i, country in enumerate(country_list):
        visited_countries[country] = highlight_colors_sampled[i]
        # Store the color of the previous country
        # if i > 0:
        #     visited_countries[country_list[i-1]] = past_country_color

        # # Set the color for the current country
        # visited_countries[country] = current_country_color

        country_shape = world[world['ADMIN'] == country]
        xmin, ymin, xmax, ymax = country_shape.total_bounds
        x_range = xmax - xmin
        y_range = ymax - ymin
        print(f'country:{country} x_range:{x_range} y_range:{y_range}')
        #if too large (wrapping around world) pick side at the edge and set it to 0.
        if x_range > 200:
            if abs(xmin) < abs(xmax):
                xmax = 20
            else:
                xmin = -20
        if y_range > 70:
            if abs(ymin) < abs(ymax):
                xmax = 20
            else:
                xmin = -20
        #recalculate x and y range
        x_range = xmax - xmin
        y_range = ymax - ymin
        if x_range < 100 :
            xmin -= buffer_percentage * x_range
            xmax += buffer_percentage * x_range
        if y_range < 50:
            ymin -= buffer_percentage * y_range
            ymax += buffer_percentage * y_range 
        #land_color = water_color
        off_set = 0
        if i %4 == 0:
            off_set = -1
        for frame in range(math.ceil(frame_duration * fps) + off_set):
            fig, ax = plt.subplots(1, 1)
            # Oscillate the color for each frame
            #water_color = oscillate_color(water_color, amplitude=10, frequency=0.01)
            
            fig.set_facecolor(water_color)

            zoom_speed = 0.15 #lower is faster
            # Calculate differences for continuous zoom
            dxmin, dymin, dxmax, dymax = (xmin - xmin_frame) / (zoom_speed*fps), (ymin - ymin_frame) / (zoom_speed*fps), (xmax - xmax_frame) / (zoom_speed*fps), (ymax - ymax_frame) / (zoom_speed*fps)


            # Update frame bounds for continuous zoom
            xmin_frame += dxmin
            ymin_frame += dymin
            xmax_frame += dxmax
            ymax_frame += dymax

            ax.set_xlim(xmin_frame, xmax_frame)
            ax.set_ylim(ymin_frame, ymax_frame)

            #set land color(in this case starting color of each ranking)
            world.plot(color=land_color, edgecolor='black', ax=ax)

            # Plot all visited countries with their respective colors
            for visited_country, color in visited_countries.items():
                visited_country_shape = world[world['ADMIN'] == visited_country]
                #color = oscillate_color(color, amplitude=10, frequency=0.01)
                visited_country_shape.plot(ax=ax, edgecolor='black', color=color)

            ax.axis('off')
            ax.set_aspect('equal')
            fig.savefig(
                f'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\maps\\map{4*fps + i*(2*fps) + frame}_{thread_id}.png', dpi=200)
            plt.close(fig)
            images.append(imageio.imread(
                f'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\maps\\map{4*fps + i*(2*fps) + frame}_{thread_id}.png'))
            # Progress update
            if (title_duration*fps + i*frame_duration*fps + frame+1) % 10 < 1:
                elapsed_time = time.time() - start_time
                minutes, seconds = divmod(elapsed_time, 60)
                estimated_minutes, estimated_seconds = divmod(total_frames-(title_duration*fps + i*frame_duration*fps + frame+1), 60)

                print(f'Frame {title_duration*fps + i*frame_duration*fps + frame+1}/{total_frames} ({100*(title_duration*fps + i*frame_duration*fps + frame+1)/total_frames:.2f}%) generated Estimated time: {int(estimated_minutes)} mins {int(estimated_seconds)} sec, Elapsed time: {int(minutes)} mins {int(seconds)} secs')

            frame_counter += 1
    #Zoom out
    xmin, ymin, xmax, ymax = -150, -70, 150, 90

    #land_color = water_color
    for frame in range(math.ceil(outro_duration * fps)): #+8
        fig, ax = plt.subplots(1, 1)
        #water_color = oscillate_color(water_color, amplitude=10, frequency=0.01)
        fig.set_facecolor(water_color)

        # Calculate differences for continuous zoom
        dxmin, dymin, dxmax, dymax = (xmin - xmin_frame) / (0.25*fps), (ymin - ymin_frame) / (0.25*fps), (xmax - xmax_frame) / (0.25*fps), (ymax - ymax_frame) / (0.25*fps)


        # Update frame bounds for continuous zoom
        xmin_frame += dxmin
        ymin_frame += dymin
        xmax_frame += dxmax
        ymax_frame += dymax

        ax.set_xlim(xmin_frame, xmax_frame)
        ax.set_ylim(ymin_frame, ymax_frame)
        world.plot(color=land_color, edgecolor='black', ax=ax)

        # Plot all visited countries with their respective colors
        for visited_country, color in visited_countries.items():
            visited_country_shape = world[world['ADMIN'] == visited_country]
            #color = oscillate_color(color, amplitude=10, frequency=0.01)
            visited_country_shape.plot(ax=ax, edgecolor='black', color=color)

        ax.axis('off')
        ax.set_aspect('equal')
        fig.savefig(
            f'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\maps\\map{4*fps + i*(2*fps) + frame}_{thread_id}.png', dpi=200)
        plt.close(fig)
        images.append(imageio.imread(
            f'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\maps\\map{4*fps + i*(2*fps) + frame}_{thread_id}.png'))
        # Progress update
        if (title_duration*fps + i*frame_duration*fps + frame+1) % 10 < 1:
            elapsed_time = time.time() - start_time
            minutes, seconds = divmod(elapsed_time, 60)
            estimated_minutes, estimated_seconds = divmod(total_frames-(title_duration*fps + i*frame_duration*fps + frame+1), 60)

            print(f'Frame {title_duration*fps + i*frame_duration*fps + frame+1}/{total_frames} ({100*(title_duration*fps + i*frame_duration*fps + frame+1)/total_frames:.2f}%) generated Estimated time: {int(estimated_minutes)} mins {int(estimated_seconds)} sec, Elapsed time: {int(minutes)} mins {int(seconds)} secs')
        frame_counter += 1

   

    # Create a video from the images
    imageio.mimsave(f'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\maps\\map_movie_{thread_id}.mp4', images, fps=fps)

if __name__ == '__main__':
    # list = [
    # "United States",
    # "Canada",
    # "United Kingdom",
    # "Germany",
    # "France",
    # "Japan",
    # "Australia",
    # "Brazil",
    # "India",
    # "China"
    # ]

    world = gpd.read_file(
        'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\src\\files\\ne_50m_admin_0_countries.shp')
    
    # Create a new GeoDataFrame with the original and shifted world
    # generate_map(list, 4, 2, 4, 'abs1231')
    print(sorted(world['ADMIN'].unique().tolist()))
    print(len(world['ADMIN'].unique().tolist()))
