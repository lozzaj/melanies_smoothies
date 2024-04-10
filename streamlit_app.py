# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col, when_matched

# Write directly to the app
st.title(":cup_with_straw: Customise your smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom smoothie!
   """)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be:', name_on_order)

session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
editable_df = st.data_editor(my_dataframe)

submitted = st.button('Submit')

if submitted:
    st.success("Someone clicked the button.", icon= "👍 ")

og_dataset = session.table("smoothies.public.orders")
edited_dataset = session.create_dataframe(editable_df)
og_dataset.merge(edited_dataset
                     , (og_dataset['name_on_order'] == edited_dataset['name_on_order'])
                     , [when_matched().update({'ORDER_FILLED': edited_dataset['ORDER_FILLED']})]
                    )

#st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe
)

if ingredients_list:
    ingredients_string = ''

for fruit_chosen in ingredients_list:
    ingredients_string += fruit_chosen + ' '

#st.write(ingredients_string)

my_insert_stmt = """ insert into smoothies.public.orders(ingredients) 
            values ('""" + ingredients_string + """','"""+name_on_order+""""')"""

st.write(my_insert_stmt)
st.stop()
time_to_insert = st.button('Submit Order')

if time_to_insert:
    session.sql(my_insert_stmt).collect()
    
    st.success('Your Smoothie is ordered "+name_on_order"!', icon="✅")

cnx = st.connection("snowflake")
session = cnx.session()

import requests
fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
# st.text(fruityvice_response.json())
fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)

