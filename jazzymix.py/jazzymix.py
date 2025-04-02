# Define the services and their prices
services = {
    "Single Track Mixing": 250,
    "EP Mixing (3-5 Tracks)": 500,
    "Album Mixing (6+ Tracks)": 650,
    "Single Track Mastering": 100,
    "EP Mastering (3-5 Tracks)": 250,
    "Album Mastering (6+ Tracks)": 500,
    "Beat Production (Instrumental Only)": 200,
    "Full Song Production": 400,
    "Full Song Prod + Mix & Master": 450,
    "Recording Session (Per Hour)": 50
}

def display_services():
    """Display available services and their prices."""
    print("Available Services:")
    for idx, (service, price) in enumerate(services.items(), start=1):
        print(f"{idx}. {service}: ${price}")

def get_user_input():
    """Get user input for service selection and details."""
    selected_services = []
    total_cost = 0

    while True:
        display_services()
        choice = input("Enter the number of the service you want to book (or 'done' to finish): ")
        
        if choice.lower() == 'done':
            break
        
        try:
            choice = int(choice)
            if 1 <= choice <= len(services):
                service_name = list(services.keys())[choice - 1]
                service_price = services[service_name]
                
                # Handle special cases where additional input is needed
                if "Tracks" in service_name:
                    num_tracks = int(input(f"How many tracks do you have for {service_name}? "))
                    if "3-5 Tracks" in service_name and (num_tracks < 3 or num_tracks > 5):
                        print("Invalid number of tracks for this service.")
                        continue
                    elif "6+ Tracks" in service_name and num_tracks < 6:
                        print("Invalid number of tracks for this service.")
                        continue
                
                elif "Recording Session" in service_name:
                    hours = int(input("How many hours do you need for the recording session? "))
                    service_price *= hours
                
                selected_services.append((service_name, service_price))
                total_cost += service_price
                print(f"Added {service_name} to your booking.")
            else:
                print("Invalid choice. Please select a valid service.")
        except ValueError:
            print("Invalid input. Please enter a number or 'done'.")
    
    return selected_services, total_cost

def collect_user_info():
    """Collect user information for booking."""
    name = input("Enter your name: ")
    email = input("Enter your email: ")
    phone = input("Enter your phone number: ")
    date = input("Enter the desired date for the appointment (YYYY-MM-DD): ")
    time = input("Enter the desired time for the appointment (HH:MM AM/PM): ")
    
    return {
        "Name": name,
        "Email": email,
        "Phone": phone,
        "Date": date,
        "Time": time
    }

def confirm_booking(user_info, selected_services, total_cost):
    """Display booking confirmation."""
    print("\n--- Booking Confirmation ---")
    print(f"User Information:")
    for key, value in user_info.items():
        print(f"{key}: {value}")
    
    print("\nSelected Services:")
    for service, price in selected_services:
        print(f"- {service}: ${price}")
    
    print(f"\nTotal Cost: ${total_cost}")
    print("Thank you for booking with us!")

def main():
    """Main function to run the booking system."""
    print("Welcome to the Music Studio Booking System!")
    
    # Get user-selected services and calculate total cost
    selected_services, total_cost = get_user_input()
    
    if not selected_services:
        print("No services selected. Booking cancelled.")
        return
    
    # Collect user information
    user_info = collect_user_info()
    
    # Confirm booking
    confirm_booking(user_info, selected_services, total_cost)

if __name__ == "__main__":
    main() 