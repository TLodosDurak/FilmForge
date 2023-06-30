import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import imageio


# Your top 10 countries list
ranking_list = ['Russia', 'USA', 'UK', 'Germany', 'France',
                'Italy', 'Spain', 'Australia', 'China', 'India']

# Load a GeoDataFrame with country shapes
world = gpd.read_file('C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\src\\files\\ne_110m_admin_0_countries_lakes.shp')
print(world.columns)
print(world[['SOVEREIGNT', 'ADMIN']].head())
# minx, miny, maxx, maxy = world.total_bounds
# print(minx, miny, maxx, maxy)


# Define colors for land and water
land_color = '#bdb67e'
water_color = '#74b3c4'



# # Filter the GeoDataFrame to only include the top 10 countries
# world['rank'] = world['ADMIN'].apply(
#     lambda x: ranking_list.index(x) + 1 if x in ranking_list else 0)



# top_10_world = world.loc[world['rank'] > 0]

# Generate the map
fig, ax = plt.subplots(1, 1)
ax.set_xlim(-70, 70)
ax.set_ylim(-30, 55)
# Remove the axis

ax.set_facecolor(water_color)

# Draw the countries
world.plot(color=land_color, edgecolor='black', ax=ax)
plt.show()


# # # Top 10 countries colored
# # top_10_world.plot(column='rank', ax=ax, cmap='cool',
# #                   legend=True, legend_kwds={'label': "Ranking"})

# # # Project to a suitable CRS before calculating centroid
# # top_10_world = top_10_world.to_crs('EPSG:3395')  # World Mercator projection

# # # Add country numbers
# # for x, y, label in zip(top_10_world.geometry.centroid.x, top_10_world.geometry.centroid.y, top_10_world['rank']):
# #     ax.text(x, y, str(label), fontsize=12)

# country_geometry = world.loc[world['ADMIN'] == 'Spain', 'geometry'].values[0]

# # Determine the bounds of the country
# minx, miny, maxx, maxy = country_geometry.bounds

# # Generate the sequence of maps
# images = []
# for i in range(72):
#     fig, ax = plt.subplots()

#     # Draw the countries
#     world.plot(color='white', edgecolor='black', ax=ax)

#     # Set the bounds for the map
#     ax.set_xlim(minx - i, maxx + i)
#     ax.set_ylim(miny - i, maxy + i)

#     # Remove the axis
#     ax.axis('off')

#     # Save the figure to a file
#     fig.savefig(f'map{i}.png')

#     # Append the image file to the images list
#     images.append(imageio.imread(f'map{i}.png'))

#     plt.close(fig)

# # Create a video from the images
# imageio.mimsave('map_movie.mp4', images, fps=24)
#plt.show()
