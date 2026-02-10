"""
Stadium Map Scraper Page - TikTik Smart Order System
עמוד הורדת מפות אצטדיון
"""

import streamlit as st
from concerts_service import fetch_venue_map_from_ticketmaster, is_ticketmaster_url
from services.concert_service import save_concert_to_favorites


def page_stadium_map_scraper():
    """Page for scraping stadium maps from TikTik website"""
    import requests
    import re
    
    st.markdown("""
    <div class="header-container">
        <h1>🗺️ הורדת מפות אצטדיון</h1>
        <p>הורד מפת אצטדיון מלינק TikTik והוסף לקבוצה</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("⬅️ חזרה לתפריט"):
        st.session_state.admin_page = None
        st.rerun()
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown("### 🔗 הדבק לינק מהאתר")
        
        tiktik_url = st.text_input("לינק לעמוד המוצר", placeholder="https://www.tiktik-online.co.il/product/...")
        
        if tiktik_url and st.button("🔍 חפש תמונות", use_container_width=True):
            try:
                response = requests.get(tiktik_url, timeout=10)
                content = response.text
                
                img_pattern = r'https://www\.tiktik-online\.co\.il/wp-content/uploads/[^\s"\'<>]+\.(svg|jpg|jpeg|png|webp)'
                all_matches = re.findall(img_pattern, content)
                
                full_pattern = r'(https://www\.tiktik-online\.co\.il/wp-content/uploads/[^\s"\'<>]+\.(?:svg|jpg|jpeg|png|webp))'
                full_urls = re.findall(full_pattern, content)
                
                exclude_words = ['logo', 'icon', 'fav', 'cropped', 'button', 'facebook', 'google', 'whatsapp', 'phone', 'search', 'arrow', 'ticket', 'airplane', 'flight', 'youtube']
                filtered_urls = []
                for url in full_urls:
                    url_lower = url.lower()
                    if not any(word in url_lower for word in exclude_words):
                        if '-300x' not in url and '-150x' not in url and '-100x' not in url:
                            filtered_urls.append(url)
                
                unique_urls = list(dict.fromkeys(filtered_urls))
                
                if unique_urls:
                    st.session_state.found_images = unique_urls
                    st.success(f"✅ נמצאו {len(unique_urls)} תמונות!")
                else:
                    st.warning("⚠️ לא נמצאו תמונות בלינק זה")
            except Exception as e:
                st.error(f"❌ שגיאה בטעינת הלינק: {str(e)}")
        
        if st.session_state.get('found_images'):
            st.markdown("### 🖼️ בחר את מפת האצטדיון")
            for i, url in enumerate(st.session_state.found_images):
                col_img, col_btn = st.columns([3, 1])
                with col_img:
                    try:
                        st.image(url, caption=url.split('/')[-1], use_container_width=True)
                    except:
                        st.write(url)
                with col_btn:
                    if st.button("✅ בחר", key=f"select_img_{i}"):
                        st.session_state.found_map_url = url
                        st.session_state.found_images = None
                        st.rerun()
        
        if st.session_state.get('found_map_url') and not st.session_state.get('found_images'):
            st.markdown("### ✅ תמונה נבחרה")
            st.image(st.session_state.found_map_url, caption="מפת האצטדיון שנבחרה", use_container_width=True)
            st.info("👈 עכשיו בחר קבוצה בצד ימין ולחץ 'שמור מפה'")
            if st.button("🔄 בחר תמונה אחרת", key="change_image"):
                st.session_state.found_map_url = None
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown("### 🏟️ בחר קבוצה/מקום")
        
        from sports_api import LEAGUES, get_teams_by_league, get_hebrew_name
        
        try:
            with open('teams_stadiums_mapping.json', 'r', encoding='utf-8') as f:
                teams_data = json.load(f)
                existing_teams = {t['id']: t for t in teams_data.get('teams', [])}
        except:
            teams_data = {'teams': []}
            existing_teams = {}
        
        category = st.radio("קטגוריה", ["⚽ כדורגל", "🎤 הופעות"], horizontal=True, key="scraper_category")
        
        team_options = {}
        selected_team_display = None
        
        if "כדורגל" in category:
            league_options = ["-- בחר ליגה --"] + list(LEAGUES.keys())
            selected_league = st.selectbox("ליגה", league_options, key="scraper_league")
            
            if selected_league and selected_league != "-- בחר ליגה --":
                english_league = LEAGUES.get(selected_league, "")
                teams = get_teams_by_league(english_league)
                
                if teams:
                    team_display_list = []
                    for t in teams:
                        team_id = t['name'].replace(" ", "_").replace("'", "").lower()
                        english_name = t['name']
                        has_map = team_id in existing_teams and existing_teams[team_id].get('map_filename')
                        status = "✅" if has_map else "❌"
                        hebrew_name = get_hebrew_name(t['name'])
                        display = f"{status} {hebrew_name} ({t['name']})"
                        team_display_list.append((display, team_id, hebrew_name, english_league, english_name))
                    
                    team_options = {t[0]: (t[1], t[2], t[3], t[4]) for t in team_display_list}
                    selected_team_display = st.selectbox("קבוצה", ["-- בחר קבוצה --"] + list(team_options.keys()), key="scraper_team")
                    if selected_team_display == "-- בחר קבוצה --":
                        selected_team_display = None
            else:
                st.info("בחר ליגה כדי לראות את הקבוצות")
        else:
            concert_venues = [
                ("תל אביב - היכל התרבות", "tel_aviv_heichal", "היכל התרבות", "Israel"),
                ("תל אביב - בלומפילד", "tel_aviv_bloomfield", "בלומפילד", "Israel"),
                ("לונדון - O2 Arena", "london_o2", "O2 Arena", "UK"),
                ("לונדון - Wembley", "london_wembley", "Wembley Stadium", "UK"),
                ("ברלין - Mercedes-Benz Arena", "berlin_mercedes", "Mercedes-Benz Arena", "Germany"),
                ("פריז - Accor Arena", "paris_accor", "Accor Arena", "France"),
                ("אמסטרדם - Ziggo Dome", "amsterdam_ziggo", "Ziggo Dome", "Netherlands"),
                ("ברצלונה - Palau Sant Jordi", "barcelona_palau", "Palau Sant Jordi", "Spain"),
                ("מילאן - San Siro", "milan_san_siro", "San Siro", "Italy"),
            ]
            all_venues = []
            for venue in concert_venues:
                venue_id = venue[1]
                has_map = venue_id in existing_teams and existing_teams[venue_id].get('map_filename')
                status = "✅" if has_map else "❌"
                all_venues.append((f"{status} {venue[0]}", venue[1], venue[0], venue[3], venue[2]))
            team_options = {v[0]: (v[1], v[2], v[3], v[4]) for v in all_venues}
            selected_team_display = st.selectbox("מקום", ["-- בחר מקום --"] + list(team_options.keys()), key="scraper_venue")
            if selected_team_display == "-- בחר מקום --":
                selected_team_display = None
        
        if st.session_state.get('found_map_url') and selected_team_display:
            team_info = team_options[selected_team_display]
            selected_team_id = team_info[0]
            team_name_he = team_info[1]
            team_league = team_info[2]
            team_name_en = team_info[3] if len(team_info) > 3 else team_name_he
            
            if st.button("💾 שמור מפה", use_container_width=True, type="primary"):
                try:
                    map_url = st.session_state.found_map_url
                    ext = map_url.split('.')[-1].split('?')[0]
                    filename = f"{selected_team_id}.{ext}"
                    filepath = f"stadium_maps/{filename}"
                    
                    response = requests.get(map_url, timeout=30)
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    if selected_team_id in existing_teams:
                        for team in teams_data['teams']:
                            if team['id'] == selected_team_id:
                                team['map_filename'] = filename
                                break
                    else:
                        new_team = {
                            'id': selected_team_id,
                            'name_en': team_name_en,
                            'name_he': team_name_he,
                            'stadium': '',
                            'stadium_he': '',
                            'city': '',
                            'city_he': '',
                            'country': '',
                            'league': team_league,
                            'map_filename': filename
                        }
                        teams_data['teams'].append(new_team)
                    
                    with open('teams_stadiums_mapping.json', 'w', encoding='utf-8') as f:
                        json.dump(teams_data, f, ensure_ascii=False, indent=2)
                    
                    st.session_state.map_save_success = f"מפת האצטדיון נשמרה בהצלחה עבור: {team_name_he}"
                    st.session_state.found_map_url = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ שגיאה בשמירה: {str(e)}")
        
        if st.session_state.get('map_save_success'):
            st.balloons()
            st.success(f"🎉 {st.session_state.map_save_success}")
            st.session_state.map_save_success = None
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📊 סיכום מפות")
    
    try:
        with open('teams_stadiums_mapping.json', 'r', encoding='utf-8') as f:
            summary_data = json.load(f)
            saved_teams = summary_data.get('teams', [])
    except:
        saved_teams = []
    
    if saved_teams:
        teams_with_maps = [t for t in saved_teams if t.get('map_filename')]
        
        st.markdown(f"**✅ יש מפה ({len(teams_with_maps)} קבוצות/מקומות)**")
        for t in teams_with_maps:
            st.markdown(f"- {t.get('name_he', t.get('id'))} ({t.get('league', '')})")

