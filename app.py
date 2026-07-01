import streamlit as st
from datetime import datetime
import requests
import nasa_api

st.set_page_config(page_title="Cosmic Explorer Hub", page_icon="🌌", layout="centered")


@st.cache_data(ttl=3600)
def load_asteroid_data():
    return nasa_api.ast.get_todays_asteroid()


def load_apod_data():
    try:
        return nasa_api.ast.get_apod()
    except:
        return None


@st.cache_data
def search_nasa_archive(query):
    url = f"https://images-api.nasa.gov/search?q={query}&media_type=image"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


today = datetime.now().strftime("%Y-%m-%d")
asteroid_data_cluster = load_asteroid_data()
apod_data_cluster = load_apod_data()

near_earth_objects = []
num_objects = 0

if asteroid_data_cluster and 'near_earth_objects' in asteroid_data_cluster:
    if today in asteroid_data_cluster['near_earth_objects']:
        near_earth_objects = asteroid_data_cluster['near_earth_objects'][today]
    num_objects = asteroid_data_cluster.get('element_count', 0)

clean_asteroids = []
for rock in near_earth_objects:
    current_rock_specs = {}
    current_rock_specs['name'] = rock.get('name', 'Unknown Rock')
    current_rock_specs['is_potentially_hazardous'] = rock.get('is_potentially_hazardous_asteroid', False)

    if rock.get('close_approach_data'):
        approach_data = rock['close_approach_data'][0]
        current_rock_specs['speed_kph'] = approach_data['relative_velocity']['kilometers_per_hour']
        current_rock_specs['miss_distance_km'] = approach_data['miss_distance']['kilometers']

        if 'estimated_diameter' in rock and 'meters' in rock['estimated_diameter']:
            current_rock_specs['size_min'] = rock['estimated_diameter']['meters']['estimated_diameter_min']
            current_rock_specs['size_max'] = rock['estimated_diameter']['meters']['estimated_diameter_max']
        else:
            current_rock_specs['size_min'] = 0.0
            current_rock_specs['size_max'] = 0.0

        clean_asteroids.append(current_rock_specs)

st.title("🌌 Cosmic Explorer Hub")
st.write("🪐 Bringing deep space archives down to Earth, simplified for humanity. ✨")

tab1, tab2, tab3 = st.tabs(["☄️ Live Asteroid Data", "📸 Astronomy Picture of The Day", "🔍 Deep Space Archive"])

with tab1:
    st.header("Live Asteroid Data")
    st.write("Tracking space rocks zooming past Earth today. Don't panic, we'll be fine... Probably.")
    st.metric(label="Total Asteroids Tracked Today", value=num_objects)
    st.markdown("---")

    if not clean_asteroids:
        st.info("No asteroid close-approach tracking sequences logged for today yet.")
    else:
        for asteroid in clean_asteroids:
            status = "⚠️ Potential Hazard" if asteroid['is_potentially_hazardous'] else "✅ No Potential Harm"
            with st.expander(f"Asteroid: {asteroid['name']} ({status})"):
                speed = float(asteroid['speed_kph'])
                distance = float(asteroid['miss_distance_km'])
                st.write(f"**Speed**: {speed:,.2f} km/h")
                st.write(f"**Misses Earth By**: {distance:,.2f} km")

                size_min = asteroid.get('size_min', 0.0)
                size_max = asteroid.get('size_max', 0.0)
                st.write(f"**Estimated Size**: {size_min:,.1f}m to {size_max:,.1f}m wide")

with tab2:
    st.header("Astronomy Picture of The Day")

    if apod_data_cluster and isinstance(apod_data_cluster, dict) and 'url' in apod_data_cluster:
        st.subheader(apod_data_cluster.get('title', 'Untitled Cosmic Wonder'))
        if apod_data_cluster.get('media_type') == 'image':
            st.image(apod_data_cluster['url'], width='stretch')
        elif apod_data_cluster.get('media_type') == 'video':
            st.video(apod_data_cluster['url'])
        st.markdown("### ✨ The Lore:")
        st.write(apod_data_cluster.get('explanation', 'No explanation provided today'))
    else:
        st.subheader("The Carina Nebula (Archive Showcase)")
        st.image("https://images-assets.nasa.gov/image/PIA25325/PIA25325~orig.jpg", width='stretch')
        st.markdown("### ✨ The Lore:")
        st.write(
            "The primary APOD feed is currently resolving network updates. Displaying a historical high-resolution archive record of the Cosmic Cliffs in the Carina Nebula, captured by the James Webb Space Telescope, to preserve application uptime.")

with tab3:
    st.header("🔍 NASA Deep Space Media Library")
    st.write(
        "Query millions of historic space exploration records directly from NASA's primary database infrastructure.")

    user_query = st.text_input("Search the cosmic archives (e.g., 'Mars Rover', 'Nebula', 'Black Hole', 'Apollo')",
                               value="Mars")

    if user_query:
        search_results = search_nasa_archive(user_query)
        if search_results and 'collection' in search_results and 'items' in search_results['collection']:
            records = search_results['collection']['items']

            if not records:
                st.warning("No media results matched your search term. Try another keywords!")

            for item in records:
                title = item['data'][0]['title']
                description = item['data'][0].get('description', 'No descriptive records attached.')
                img_url = item['links'][0]['href'] if 'links' in item else None

                if img_url:
                    st.subheader(title)
                    st.image(img_url, width='stretch')
                    with st.expander("Read Historical Record Log"):
                        st.write(description)
                    st.markdown("---")
        else:
            st.error("The NASA Media database is currently undergoing maintenance. Try again in a minute!")
