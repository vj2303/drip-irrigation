import pygsheets
import pandas as pd

gc = pygsheets.authorize(service_file='creds.json')

# Define the data
data = [
    {
      "pic_url": "https://media.istockphoto.com/id/962353378/vector/fast-food-line-icon.jpg?s=612x612&w=0&k=20&c=xD9-KlVj_w4hqhlB6VnsnTqcaumATgDnywNdhrhOok4=",
      "productName": "Masala Dosa",
      "productPrice": "120",
      "productTotalPrice": 240,
      "quantity": 2,
      "username": "testUser"
    },
    {
      "pic_url": "https://media.istockphoto.com/id/962353378/vector/fast-food-line-icon.jpg?s=612x612&w=0&k=20&c=xD9-KlVj_w4hqhlB6VnsnTqcaumATgDnywNdhrhOok4=",
      "productName": "Soda",
      "productPrice": "40",
      "productTotalPrice": 80,
      "quantity": 2,
      "username": "testUser"
    },
    {
      "pic_url": "https://media.istockphoto.com/id/962353378/vector/fast-food-line-icon.jpg?s=612x612&w=0&k=20&c=xD9-KlVj_w4hqhlB6VnsnTqcaumATgDnywNdhrhOok4=",
      "productName": "Pizza",
      "productPrice": "200",
      "productTotalPrice": 600,
      "quantity": 3,
      "username": "testUser"
    }
]

df = pd.DataFrame(data)
sh = gc.open('Stall-management-data')
wks = sh[0]
existing_data = wks.get_all_records()
combined_data = existing_data + data
df_combined = pd.DataFrame(combined_data)
wks.set_dataframe(df_combined, start='A1')
