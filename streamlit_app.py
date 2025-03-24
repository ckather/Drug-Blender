import streamlit as st
import pandas as pd
import os

# ===================================================
# 1) FOUR SAMPLE CSVs (EACH HAS unique_id + Data)
# ===================================================

SAMPLE1_CSV = """unique_id,Data
1,Apple
2,Banana
3,Cherry
4,Durian
5,Elderberry
6,Fig
7,Grape
8,Honeydew
9,Kiwi
10,Lemon
11,Mango
12,Nectarine
13,Orange
14,Papaya
15,Quince
16,Raspberry
17,Strawberry
18,Tangerine
19,Ugli
20,Vanilla
21,Watermelon
22,Xigua
23,Yam
24,Zucchini
25,Almond
26,Brazilnut
27,Cashew
28,Date
29,Eggplant
30,Feijoa
31,Guava
32,Huckleberry
33,Ilama
34,Jujube
35,Kumquat
36,Lime
37,Mandarin
38,Nance
39,Olive
40,Pineapple
41,Quandong
42,Rambutan
43,Soursop
44,Tamarind
45,Ube
46,Voavanga
47,Waxapple
48,Ximenia
49,Yuzu
50,Zigzagvine
51,Avocado
52,Bilberry
53,Cloudberry
54,Dragonfruit
55,Elderflower
56,Fingerlime
57,Goumi
58,Hawthorn
59,Imbe
60,Jabuticaba
61,Kiwano
62,Lingonberry
63,Mulberry
64,Naranjilla
65,Ogen
66,Pawpaw
67,Redcurrant
68,Salal
69,Tamarillo
70,Uvilla
71,Vogelberry
72,Whitecurrant
73,Xanthium
74,Yantok
75,Zigzagfruit
76,Apricot
77,Blackberry
78,Cantaloupe
79,Damson
80,Emuberry
81,Feijoa2
82,Galia
83,Honeycrisp
84,Indianfig
85,Jackfruit
86,Kaffir
87,Lychee
88,Mamey
89,Noni
90,Orach
91,Persimmon
92,Quray
93,Roseapple
94,Sapodilla
95,Tayberry
96,Ugniberry
97,Voavanga2
98,WhiteSapote
99,Xoconostle
100,Yellowpassion
"""

SAMPLE2_CSV = """unique_id,Data
1,Desk
2,Chair
3,Table
4,Lamp
5,Sofa
6,Shelf
7,Stool
8,Bed
9,Dresser
10,Mirror
11,Rug
12,Closet
13,Cabinet
14,Couch
15,Ottoman
16,Counter
17,Bench
18,Frame
19,Bookcase
20,Drawer
21,Partition
22,Safe
23,Stand
24,Rack
25,Podium
26,Cart
27,CoatTree
28,Headboard
29,Nightstand
30,Vanity
31,Recliner
32,Buffet
33,Sideboard
34,Hutch
35,Credenza
36,Footstool
37,Futon
38,Hamper
39,Chest
40,Wardrobe
41,Trunk
42,Panel
43,Bin
44,Basket
45,Cradle
46,Playpen
47,Armoire
48,Loveseat
49,Cube
50,Bench2
51,Bunkbed
52,Chaise
53,Diwan
54,EntertainmentCenter
55,FoldableTable
56,Glider
57,Hatstand
58,IroningBoard
59,Jumper
60,Kneeler
61,Locker
62,MosesBasket
63,NestingTables
64,Organ
65,Partition2
66,QuiltRack
67,RoomDivider
68,Stepstool
69,Teepee
70,UmbrellaStand
71,Valet
72,WineRack
73,XBench
74,Yardbench
75,ZenChair
76,CornerShelf
77,DiningTable
78,OfficeChair
79,PatioChair
80,RockingChair
81,SwivelChair
82,TaskChair
83,Throne
84,VisitorChair
85,WingChair
86,WritingDesk
87,ZtypeDesk
88,ZeroGravityChair
89,AcousticPanel
90,BeanBag
91,ConvertibleSofa
92,DeckChair
93,EggChair
94,FloorCushion
95,GhostChair
96,Hammock
97,InflatableChair
98,JetChair
99,KneelingChair
100,LoungeChair
"""

SAMPLE3_CSV = """unique_id,Data
1,Red
2,Green
3,Blue
4,Yellow
5,Orange
6,Purple
7,Brown
8,Gray
9,Black
10,White
11,Beige
12,Crimson
13,Teal
14,Cyan
15,Magenta
16,Gold
17,Silver
18,Maroon
19,Navy
20,Lime
21,Olive
22,Aqua
23,Coral
24,Fuchsia
25,Indigo
26,Khaki
27,Plum
28,RosyBrown
29,Sienna
30,Salmon
31,Tomato
32,Turquoise
33,Violet
34,Azure
35,Beige2
36,Bisque
37,BlanchedAlmond
38,Chartreuse
39,Chocolate
40,CornflowerBlue
41,Cornsilk
42,DarkBlue
43,DarkCyan
44,DarkGoldenRod
45,DarkGray
46,DarkGreen
47,DarkKhaki
48,DarkMagenta
49,DarkOliveGreen
50,DarkOrange
51,DarkOrchid
52,DarkRed
53,DarkSalmon
54,DarkSeaGreen
55,DarkSlateBlue
56,DarkSlateGray
57,DarkTurquoise
58,DarkViolet
59,DeepPink
60,DeepSkyBlue
61,DimGray
62,DodgerBlue
63,FireBrick
64,FloralWhite
65,ForestGreen
66,Gainsboro
67,GhostWhite
68,Gold2
69,GoldenRod
70,GreenYellow
71,HoneyDew
72,HotPink
73,IndianRed
74,Ivory
75,Khaki2
76,Lavender
77,LawnGreen
78,LemonChiffon
79,LightBlue
80,LightCoral
81,LightCyan
82,LightGoldenRod
83,LightGray
84,LightGreen
85,LightPink
86,LightSalmon
87,LightSeaGreen
88,LightSkyBlue
89,LightSlateGray
90,LightSteelBlue
91,LightYellow
92,LimeGreen
93,Linen
94,MediumAquamarine
95,MediumBlue
96,MediumOrchid
97,MediumPurple
98,MediumSeaGreen
99,MediumSlateBlue
100,MediumSpringGreen
"""

SAMPLE4_CSV = """unique_id,Data
1,Alpha
2,Bravo
3,Charlie
4,Delta
5,Echo
6,Foxtrot
7,Golf
8,Hotel
9,India
10,Juliet
11,Kilo
12,Lima
13,Mike
14,November
15,Oscar
16,Papa
17,Quebec
18,Romeo
19,Sierra
20,Tango
21,Uniform
22,Victor
23,Whiskey
24,XRay
25,Yankee
26,Zulu
27,Alpha2
28,Bravo2
29,Charlie2
30,Delta2
31,Echo2
32,Foxtrot2
33,Golf2
34,Hotel2
35,India2
36,Juliet2
37,Kilo2
38,Lima2
39,Mike2
40,November2
41,Oscar2
42,Papa2
43,Quebec2
44,Romeo2
45,Sierra2
46,Tango2
47,Uniform2
48,Victor2
49,Whiskey2
50,XRay2
51,Yankee2
52,Zulu2
53,Alpha3
54,Bravo3
55,Charlie3
56,Delta3
57,Echo3
58,Foxtrot3
59,Golf3
60,Hotel3
61,India3
62,Juliet3
63,Kilo3
64,Lima3
65,Mike3
66,November3
67,Oscar3
68,Papa3
69,Quebec3
70,Romeo3
71,Sierra3
72,Tango3
73,Uniform3
74,Victor3
75,Whiskey3
76,XRay3
77,Yankee3
78,Zulu3
79,Alpha4
80,Bravo4
81,Charlie4
82,Delta4
83,Echo4
84,Foxtrot4
85,Golf4
86,Hotel4
87,India4
88,Juliet4
89,Kilo4
90,Lima4
91,Mike4
92,November4
93,Oscar4
94,Papa4
95,Quebec4
96,Romeo4
97,Sierra4
98,Tango4
99,Uniform4
100,Victor4
"""

# ===================================================
# 2) STREAMLIT APP WITH DOWNLOAD & UPLOAD
# ===================================================

st.title("Drug Blender: Exactly 3 Columns & 400 Rows")

st.write(
    "Below, you can download **4 sample CSV files**. Each has 2 columns: `unique_id` and `Data`, "
    "with 100 rows each. When you upload them, the app will simply **append** (not merge) them, "
    "sort by `unique_id`, and color-code each file's rows. You'll end up with exactly **400 rows** "
    "and **3 columns**: `unique_id`, `Data`, `source_file`."
)

# --- Provide download buttons for each CSV ---
st.download_button("Download sample1.csv", SAMPLE1_CSV, "sample1.csv", "text/csv")
st.download_button("Download sample2.csv", SAMPLE2_CSV, "sample2.csv", "text/csv")
st.download_button("Download sample3.csv", SAMPLE3_CSV, "sample3.csv", "text/csv")
st.download_button("Download sample4.csv", SAMPLE4_CSV, "sample4.csv", "text/csv")

st.write("---")

# --- File uploader ---
uploaded_files = st.file_uploader(
    "Upload up to 5 CSV files (but for exactly 400 rows, use the 4 above). Each must have columns `unique_id` & `Data`.",
    type=["csv"],
    accept_multiple_files=True
)

# --- If files uploaded, process them ---
if uploaded_files:
    if len(uploaded_files) > 5:
        st.error("Please upload a maximum of 5 files.")
    else:
        # Color palette (up to 5 files)
        color_palette = ["#FFCFCF", "#CFFFCF", "#CFCFFF", "#FFFACF", "#FFCFFF"]
        color_map = {}
        
        df_list = []
        for i, file in enumerate(uploaded_files):
            # Read CSV
            df = pd.read_csv(file)
            
            # Ensure columns are exactly [unique_id, Data]
            expected_cols = {"unique_id", "Data"}
            actual_cols = set(df.columns)
            if not expected_cols.issubset(actual_cols):
                st.error(f"File {file.name} does not have the required columns: {expected_cols}")
                st.stop()
            
            # Add a source_file column
            df["source_file"] = file.name
            color_map[file.name] = color_palette[i]
            
            df_list.append(df)
        
        # Concatenate the dataframes
        master_df = pd.concat(df_list, ignore_index=True)
        
        # Sort by unique_id so we see 1,1,1,1, then 2,2,2,2, etc.
        master_df = master_df.sort_values(by="unique_id", ignore_index=True)
        
        # Check final shape
        st.write(f"**Combined DataFrame shape:** {master_df.shape}")
        st.write("**Columns:**", list(master_df.columns))
        
        # Display legend
        st.write("**Legend (File → Color):**")
        for fname, c in color_map.items():
            st.markdown(f"<span style='background-color:{c};padding:4px 8px;'>{fname}</span>", unsafe_allow_html=True)
        
        # Color rows based on source_file
        def color_rows_by_source(row):
            return [f"background-color: {color_map[row['source_file']]}" for _ in row]
        
        styled_df = master_df.style.apply(color_rows_by_source, axis=1)
        
        st.write("**Preview of Combined & Sorted Data:**")
        st.write(styled_df.to_html(), unsafe_allow_html=True)

        # Optional numeric summary (though these samples have no numeric columns except unique_id)
        numeric_cols = master_df.select_dtypes(include=["int", "float"]).columns
        if len(numeric_cols) > 0:
            st.subheader("Numeric Column Summaries")
            st.write(master_df.describe())
        
else:
    st.info("No files uploaded yet. Download the sample CSVs above, then re-upload them here.")
