import json
import PySimpleGUI as sg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from datetime import datetime, timedelta

# Define the window title and file paths
windowTitle = 'Health & Fitness'
titlebarIcon = 'icon.png'
strengthFile = 'strength.json'
cardioFile = 'cardio.json'
meditationFile = 'meditation.json'
weightFile = 'weight.json'

# Set the theme for the GUI
sg.theme('Python Plus')

def readFile(filename, list1, window):
    """
    Function to read a file and load its content.
    If the file is empty, it prints 'Empty' to the window output.
    """
    try:
        with open(filename, 'r') as f:
            list1 = json.load(f)
            return list1
    except json.decoder.JSONDecodeError:
        window['-OUTPUT-'].print('Empty')
        return []

def writeFile(filename, list):
    """
    Function to write a list into a file.
    """
    with open(filename, 'w') as f:
        json.dump(list, f)

def add_entry(window, list, file, entry):
    """
    Function to add an entry to a list and write it to a file.
    If the input is invalid, it shows a popup with 'Invalid Input'.
    """
    try:
        list.append(entry)
        writeFile(file, list)
        window.un_hide()
    except:
        sg.popup('Invalid Input', font=(0,10), no_titlebar=True)
        window.un_hide()

def delete_entry(window, list, file):
    """
    Function to delete an entry from a list and update the file.
    If the input is invalid, it shows a popup with 'Invalid Input'.
    """
    try:
        window.hide()
        entry = sg.PopupGetText('Number: ')
        if entry == None:
            pass
        else:
            list.remove(list[int(entry) -1])
            for i in range(len(list)):
                list[i]['number'] = i+1
            writeFile(file, list)
        window.un_hide()
    except:
        sg.popup('Invalid Input', font=(0,10), no_titlebar=True)
        window.un_hide()


def strength():
    """
    Opens the strength training GUI.

    This function creates the GUI window for strength training,
    including the main menu, options menu, and output window.
    It also creates the graph for exercise progress.
    """
    open_strength()
    # Declare Variables
    strengthList = []
    global strengthFig
    toolbar = None
    canvas_agg = None
    weight_repsList = []
    selected_exercise = 0
    default_exercise = ''
    
    while True:
        datePerExercise = []
        # Read file to list
        strengthList = readFile(strengthFile, strengthList, strengthWindow) 
        number = len(strengthList) + 1 
        # Create graph
        strengthFig, ax = plt.subplots() 
        # Create a set of exercises so they won't be reused to label in the graph
        exercises = set(i['exercise'] for i in strengthList) 

        for exercise in exercises:
            # Get data for this exercise
            exercise_data = [i for i in strengthList if i['exercise'] == exercise]  
            # Get each date for the exercise
            dates = [datetime.strptime(i['date'], '%m-%d-%Y') for i in exercise_data] 
            # Get the strength level for the exercises
            weights_reps = [float(float(i['weight']) * float(i['reps']) / 10) for i in exercise_data] 
            # Plot the exercise
            ax.plot(dates, weights_reps, marker='o', label=exercise) 
            weight_repsList.append(weights_reps)
            datePerExercise.append(dates)

        for i in strengthList:
            strengthWindow['-OUTPUT-'].print(f'{i['number']}. {i['exercise']}: {i['weight']} Lbs, {i['reps']} Reps        -        {i['date']}')

        # Conversion from set to list
        exercises = list(exercises) 
        # Change default exercise for option menu
        if default_exercise == '': 
            default_exercise = exercises[len(exercises)-1]
        # Update option menu
        strengthWindow['OPTIONS'].update(values=exercises, value=default_exercise) 


        # Get the days average
        current_date = datetime.today()
        week_ago = current_date - timedelta(days=7)
        current_date = datetime.today()
        weeks_ago = current_date - timedelta(days=30)
        weekly = 0.0
        divid = 0
        weekly2 = 0.0
        divid2 = 0
        try:
            weights_reps = weight_repsList[selected_exercise]
            
        except:
            pass
        dates = datePerExercise[selected_exercise]
        for i in range(len(dates)):
            if week_ago <= dates[i] <= current_date:
                weekly += weights_reps[i]
                divid+=1
        for i in range(len(dates)):
            if weeks_ago <= dates[i] <= current_date:
                weekly2 += weights_reps[i]
                divid2+=1
        if divid == 0:
            divid = 1
        if divid2 == 0:
            divid2 = 1
        strengthWindow['WEEKLY'].update(f'7 Day Average: {weekly/divid}\n30 Day Average: {weekly2/divid2}')


        # Format the x axis to use date time
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d-%Y')) 
        start_date = datetime(2024, 1, 17)  # Start date
        end_date = datetime.today()  # End date
        ax.set_xlim(start_date, end_date) # Limit the x axis
        strengthFig.autofmt_xdate() # Update the graph
        plt.title('Exercise Progress') # Title
        plt.xlabel('Date') # X Label
        plt.ylabel('Strength') # Y Label
        plt.legend() # Legend
        plt.grid() # Grid

        if canvas_agg: # If graph exists, delete graph. (For updating graph)
            canvas_agg.get_tk_widget().forget()
            toolbar.forget()
        # Create graph
        canvas_agg = FigureCanvasTkAgg(strengthFig, master=strengthWindow['-CANVAS-'].TKCanvas) 
        # Create toolbar
        toolbar = NavigationToolbar2Tk(canvas_agg, strengthWindow['-CANVAS-'].TKCanvas) 
        toolbar.update() # Update toolbar
        canvas_agg.draw() # Draw graph

        canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1) # Fill canvas with graph

        # Read event from GUI input
        event, values = strengthWindow.read() 
        strengthWindow['-OUTPUT-'].update('')
        try:
            selected_exercise = exercises.index(values['OPTIONS'])
        except:
            selected_exercise = ''
        weight_repsList = []

        try:
            default_exercise = exercises[exercises.index(values['OPTIONS'])]
        except:
            pass

        if event == 'Weight':
            strengthWindow.close()
            main_menu()
        elif event == 'Cardio':
            strengthWindow.close()
            cardio()
        elif event == 'Meditation':
            strengthWindow.close()
            meditation()
        if event == 'Add Entry':
            strengthWindow['-OUTPUT-'].update('')
            strengthWindow.hide()
            entry1 = sg.PopupGetText('Exercise: ')
            if entry1 == None:
                strengthWindow.un_hide()
                pass
            else:
                entry2 = sg.PopupGetText('Weight: ')
                if entry2 == None:
                    strengthWindow.un_hide()
                    pass  
                else:
                    entry3 = sg.PopupGetText('Reps: ')
                    if entry3 == None:
                        strengthWindow.un_hide()
                        pass
                    else:
                        entry = {
                            'number': number,
                            'exercise': entry1.upper(),
                            'weight': entry2,
                            'reps': entry3,
                            'date': datetime.today().strftime('%m-%d-%Y')
                        }
                        add_entry(strengthWindow, strengthList, strengthFile, entry)
        elif event == 'Delete Entry':
            strengthWindow['-OUTPUT-'].update('')
            delete_entry(strengthWindow, strengthList, strengthFile)
        elif event == 'Exit' or sg.WIN_CLOSED:
            strengthWindow.close()
            exit()

def cardio():
    """
    This function displays a cardio progress window with a graph and data.

    It allows users to add new entries, delete entries, and navigate to other fitness applications.
    """

    # Open cardio file and initialize variables
    open_cardio()
    cardioList = []
    global cardioFig
    canvas_agg = None
    toolbar = None

    while True:
        # Read data from cardio file and update list
        cardioList = readFile(cardioFile, cardioList, cardioWindow)
        number = len(cardioList) + 1

        # Create figure and subplots for the graph
        cardioFig, ax = plt.subplots()
        dates = []
        speeds = []
        distances = []
        times = []

        # Iterate through each entry in the list
        for i in cardioList:
            # Add leading zero to seconds if needed
            if len(i['seconds']) == 1:
                i['seconds'] = f'0{i['seconds']}'

            # Calculate speed and print data to output window
            speed = float(float(i['distance']) / (float(i['minutes']) + (float(i['seconds']) / 60)) * 60)
            cardioWindow['-OUTPUT-'].print(f'{i["number"]}. {i["distance"]} Miles: {i["minutes"]}:{i["seconds"]}, {round(speed, 2)} MPH        -        {i["date"]}')

            # Convert date to datetime object and append data to lists
            date = datetime.strptime(i['date'], '%m-%d-%Y')
            dates.append(date)
            speeds.append(speed)
            distances.append(float(i['distance']))
            times.append(float(i['minutes']) + (float(i['seconds']) / 60))

        # Calculate weekly and monthly averages
        current_date = datetime.today()
        week_ago = current_date - timedelta(days=7)
        current_date = datetime.today()
        weeks_ago = current_date - timedelta(days=30)
        weekly = 0.0
        divid = 0
        weekly2 = 0.0
        divid2 = 0
        weeklyD = 0.0
        weeklyD2 = 0.0
        weeklyT = 0.0
        weeklyT2 = 0.0

        for i in range(len(dates)):
            if week_ago <= dates[i] <= current_date:
                weekly += speeds[i]
                weeklyD += distances[i]
                weeklyT += times[i]
                divid += 1
        for i in range(len(dates)):
            if weeks_ago <= dates[i] <= current_date:
                weekly2 += speeds[i]
                weeklyD2 += distances[i]
                weeklyT2 += times[i]
                divid2 += 1

        if divid == 0:
            divid = 1
        if divid2 == 0:
            divid2 = 1

        # Update weekly and monthly average text in window
        cardioWindow['WEEKLY'].update(f'7 Day Average:   {round(weeklyD/divid, 2)} Miles:   {round(weeklyT/divid, 2)} Minutes,   {round(weekly/divid, 2)} MPH\n30 Day Average:   {round(weeklyD2/divid2, 2)} Miles:   {round(weeklyT2/divid2, 2)} Minutes,   {round(weekly2/divid2, 2)} MPH')

        # Create line plots for speed, distance, and time
        ax.plot(dates, speeds, marker='o', label='Speed')
        ax.plot(dates, distances, marker='v', label='Distance')
        ax.plot(dates, times, marker='s', label='Time')

        # Set axis formatting and limits
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d-%Y'))
        cardioFig.autofmt_xdate()
        start_date = datetime(2024, 1, 17)
        end_date = datetime.today()
        ax.set_ylim(0)
        ax.set_xlim(start_date, end_date)

        # Set title, labels, and grid
        plt.title('Cardio Progress')
        plt.xlabel('Date')
        plt.ylabel('Speed/Distance/Time')
        plt.legend()
        plt.grid()

        # Update and display the plot
        if canvas_agg:
            # Remove old plot and toolbar
            canvas_agg.get_tk_widget().forget()
            toolbar.forget()

        # Create new canvas and toolbar
        canvas_agg = FigureCanvasTkAgg(cardioFig, master=cardioWindow['-CANVAS-'].TKCanvas)
        canvas_agg.draw()
        toolbar = NavigationToolbar2Tk(canvas_agg, cardioWindow['-CANVAS-'].TKCanvas)
        toolbar.update()

        # Pack the canvas widget
        canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)

        # Read user event from window
        event, values = cardioWindow.read()

        # Handle button clicks
        if event == 'Strength':
            # Close cardio window and open strength window
            cardioWindow.close()
            strength()
        elif event == 'Weight':
            # Close cardio window and open main menu
            cardioWindow.close()
            main_menu()
        elif event == 'Meditation':
            # Close cardio window and open meditation window
            cardioWindow.close()
            meditation()
        elif event == 'Add Entry':
            # Clear output window and hide cardio window
            cardioWindow['-OUTPUT-'].update('')
            cardioWindow.hide()

            # Get distance input from user
            entry1 = sg.PopupGetText('Distance in miles: ')

            # Validate distance input
            if entry1 is None or not entry1.replace('.', '', 1).isdigit():
                # Show error message and unhide window
                cardioWindow.un_hide()
                pass
            else:
                # Get minutes input from user
                entry2 = sg.PopupGetText('Minutes: ')

                # Validate minutes input
                if entry2 is None or not entry2.isdigit():
                    # Show error message and unhide window
                    cardioWindow.un_hide()
                    pass
                else:
                    # Get seconds input from user
                    entry3 = sg.PopupGetText('Seconds: ')

                    # Validate seconds input
                    if entry3 is None or not entry3.isdigit():
                        # Show error message and unhide window
                        cardioWindow.un_hide()
                        pass
                    else:
                        # Create new entry dictionary
                        entry = {
                            'number': number,
                            'distance': entry1,
                            'minutes': entry2,
                            'seconds': entry3,
                            'date': datetime.today().strftime('%m-%d-%Y')
                        }

                        # Add entry to list and update file
                        add_entry(cardioWindow, cardioList, cardioFile, entry)

        elif event == 'Delete Entry':
            # Clear output window and delete entry
            cardioWindow['-OUTPUT-'].update('')
            delete_entry(cardioWindow, cardioList, cardioFile)
        elif event == 'Exit' or sg.WIN_CLOSED:
            # Close cardio window and exit program
            cardioWindow.close()
            exit()

def meditation():
    """
    This function displays a meditation progress window with a graph and data.

    It allows users to add new entries, delete entries, and navigate to other fitness applications.
    """

    # Open meditation file and initialize variables
    open_meditation()
    meditationList = []
    global meditationFig
    canvas_agg = None
    toolbar = None

    while True:
        # Read data from meditation file and update list
        meditationList = readFile(meditationFile, meditationList, meditationWindow)
        number = len(meditationList) + 1

        # Create figure and subplots for the graph
        meditationFig, ax = plt.subplots()
        dates = []
        ratings = []
        times = []

        # Iterate through each entry in the list
        for i in meditationList:
            # Print data to output window
            meditationWindow['-OUTPUT-'].print(f'{i["number"]}. {i["rating"]}/10:   {i["length"]} Minutes,   {i["position"]}, {i["inorout"]}, {i["sound"]}        -        {i["date"]}')

            # Convert date to datetime object and append data to lists
            date = datetime.strptime(i['date'], '%m-%d-%Y')
            rating = float(i['rating'])
            time = float(i['length'])
            dates.append(date)
            ratings.append(rating)
            times.append(time)

        # Calculate weekly and monthly averages
        current_date = datetime.today()
        week_ago = current_date - timedelta(days=7)
        current_date = datetime.today()
        weeks_ago = current_date - timedelta(days=30)
        weekly = 0.0
        divid = 0
        weekly2 = 0.0
        divid2 = 0
        weeklyT = 0.0
        weeklyT2 = 0.0

        for i in range(len(dates)):
            if week_ago <= dates[i] <= current_date:
                weekly += ratings[i]
                weeklyT += times[i]
                divid += 1
        for i in range(len(dates)):
            if weeks_ago <= dates[i] <= current_date:
                weekly2 += ratings[i]
                weeklyT2 += times[i]
                divid2 += 1

        if divid == 0:
            divid = 1
        if divid2 == 0:
            divid2 = 1

        # Update weekly and monthly average text in window
        meditationWindow['WEEKLY'].update(f'7 Day Average:   {round(weekly/divid, 2)}/10:   {round(weeklyT/divid, 2)} Minutes\n30 Day Average:   {round(weekly2/divid2, 2)}/10:   {round(weeklyT2/divid2, 2)} Minutes')

        # Create line plots for ratings and time
        ax.plot(dates, ratings, marker='o', label='Rating')
        ax.plot(dates, times, marker='s', label='Minutes')

        # Set axis formatting and limits
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d-%Y'))
        meditationFig.autofmt_xdate()
        start_date = datetime(2024, 1, 17)
        end_date = datetime.today()
        ax.set_ylim(0)
        ax.set_xlim(start_date, end_date)

        # Set title, labels, and grid
        plt.title('Meditation Ratings')
        plt.xlabel('Date')
        plt.ylabel('Rating & Minutes')
        plt.legend()
        plt.grid()

        # Update and display the plot
        if canvas_agg:
            # Remove old plot and toolbar
            canvas_agg.get_tk_widget().forget()
            toolbar.forget()

        # Create new canvas and toolbar
        canvas_agg = FigureCanvasTkAgg(meditationFig, master=meditationWindow['-CANVAS-'].TKCanvas)
        canvas_agg.draw()
        toolbar = NavigationToolbar2Tk(canvas_agg, meditationWindow['-CANVAS-'].TKCanvas)
        toolbar.update()
        canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)

        # Read user event from window
        event, values = meditationWindow.read()

        # Handle button clicks
        if event == 'Strength':
            # Close meditation window and open strength window
            meditationWindow.close()
            strength()
        elif event == 'Cardio':
            # Close meditation window and open cardio window
            meditationWindow.close()
            cardio()
        elif event == 'Weight':
            # Close meditation window and open main menu
            meditationWindow.close()
            main_menu()
        elif event == 'Add Entry':
            # Clear output window and hide meditation window
            meditationWindow['-OUTPUT-'].update('')
            meditationWindow.hide()

            # Get rating input from user
            entry1 = sg.PopupGetText('Rating from 0 - 10: ')

            # Validate rating input
            if entry1 is None or not entry1.replace('.', '', 1).isdigit() or int(entry1) < 0 or int(entry1) > 10:
                # Show error message and unhide window
                meditationWindow.un_hide()
                pass
            else:
                # Get length input from user
                entry2 = sg.PopupGetText('Length in minutes: ')

                # Validate length input
                if entry2 is None or not entry2.replace('.', '', 1).isdigit():
                    # Show error message and unhide window
                    meditationWindow.un_hide()
                    pass
                else:
                    # Open window to choose sitting or laying position
                    entry3Window = sg.Window('Sitting or Laying?', layout=[[sg.Button('Sitting'), sg.Button('Laying'), sg.Button('Cancel')]])
                    entry3, values = entry3Window.read()
                    entry3Window.close()

                    # If user cancels, unhide the meditation window
                    if entry3 == 'Cancel':
                        meditationWindow.un_hide()
                        pass
                    else:
                        # If laying, ask if it was yesterday
                        yesterday = 'No'
                        if entry3 == 'Laying':
                            yesterday = sg.popup_yes_no('Was the meditation yesterday?')

                        # Open window to choose sound type
                        entry4Window = sg.Window('Sound?', layout=[[sg.Button('Music'), sg.Button('Ambience'), sg.Button('Music + Ambience'), sg.Button('Silent'), sg.Button('Guided'), sg.Button('Cancel')]])
                        entry4, values = entry4Window.read()
                        entry4Window.close()

                        # If user cancels, unhide the meditation window
                        if entry4 == 'Cancel':
                            meditationWindow.un_hide()
                            pass
                        else:
                            # Open window to choose inside or outside location
                            entry5Window = sg.Window('Inside or Outside?', layout=[[sg.Button('Inside'), sg.Button('Outside'), sg.Button('Cancel')]])
                            entry5, values = entry5Window.read()
                            entry5Window.close()

                            # If user cancels, unhide the meditation window
                            if entry5 == 'Cancel':
                                meditationWindow.un_hide()
                                pass
                            else:
                                # Create new entry dictionary with user input
                                entry = {
                                    'number': number,
                                    'rating': entry1,
                                    'length': entry2,
                                    'position': entry3,
                                    'sound': entry4,
                                    'inorout': entry5,
                                    'date': datetime.today().strftime('%m-%d-%Y')
                                }

                                # If meditation was yesterday, update date
                                if yesterday == 'Yes':
                                    entry['date'] = (datetime.today() - timedelta(days=1)).strftime('%m-%d-%Y')

                                # Add entry to list and update file
                                add_entry(meditationWindow, meditationList, meditationFile, entry)

        elif event == 'Delete Entry':
            # Clear output window and delete entry
            meditationWindow['-OUTPUT-'].update('')
            delete_entry(meditationWindow, meditationList, meditationFile)
        elif event == 'Exit' or sg.WIN_CLOSED:
            # Close meditation window and exit program
            meditationWindow.close()
            exit()



def main_menu():
    """
    This function is the main entry point for the fitness application, displaying the user interface and handling interactions.

    It presents the user with a weight progress graph, weight data, and buttons to navigate to other fitness sections like strength training, cardio, and meditation.
    Additionally, it allows users to add new weight entries and delete existing ones.
    """

    # Open the main menu window and initialize variables
    open_mainmenu()
    weightList = []  # Stores weight entries as dictionaries
    global weight_fig # Global variable for graph
    toolbar, canvas_agg = None, None

    while True:
        # Read weight data from file and update list
        weightList = readFile(weightFile, weightList, mainmenuWindow)
        next_entry_number = len(weightList) + 1  # Calculate next entry's ID

        # Create a new figure and axes for the weight graph
        weight_fig, ax = plt.subplots()
        dates, weights = [], []  # Lists to store data points

        # Extract and format data from each weight entry
        for entry in weightList:
            mainmenuWindow['-OUTPUT-'].print(f"{entry['number']}. {entry['weight']} Lbs - {entry['date']}")
            date_obj = datetime.strptime(entry['date'], '%m-%d-%Y')
            weight_value = float(entry['weight'])
            dates.append(date_obj)
            weights.append(weight_value)

        # Calculate weekly and monthly weight averages
        current_date = datetime.today()
        week_ago = current_date - timedelta(days=7)
        month_ago = current_date - timedelta(days=30)
        weekly_sum, weekly_count = 0.0, 0
        monthly_sum, monthly_count = 0.0, 0
        for i in range(len(dates)):
            if week_ago <= dates[i] <= current_date:
                weekly_sum += weights[i]
                weekly_count += 1
            if month_ago <= dates[i] <= current_date:
                monthly_sum += weights[i]
                monthly_count += 1

        # Prevent division by zero
        weekly_count = max(weekly_count, 1)
        monthly_count = max(monthly_count, 1)

        # Update the text elements displaying averages
        mainmenuWindow['WEEKLY'].update(f'7 Day Average: {weekly_sum / weekly_count}\n30 Day Average: {monthly_sum / monthly_count}')

        # Create a line plot showing weight history
        ax.plot(dates, weights, marker='o')

        # Set axis formatting and limits for readability
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d-%Y'))
        weight_fig.autofmt_xdate()
        start_date = datetime(2024, 1, 17)  # Assuming weight data starts from this date
        ax.set_xlim(start_date, datetime.today())
        plt.title('Weight History')
        plt.xlabel('Date')
        plt.ylabel('Weight (Lbs)')
        plt.legend()
        plt.grid()

        # Update the weight graph if it already exists
        if canvas_agg:
            canvas_agg.get_tk_widget().forget()  # Remove old canvas
            toolbar.forget()  # Remove old toolbar

        # Create a new canvas and navigation toolbar for the graph
        canvas_agg = FigureCanvasTkAgg(weight_fig, master=mainmenuWindow['-CANVAS-'].TKCanvas)
        canvas_agg.draw()
        toolbar = NavigationToolbar2Tk(canvas_agg, mainmenuWindow['-CANVAS-'].TKCanvas)
        toolbar.update()

        # Pack the canvas widget to display the graph
        canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)

        # Read the user's choice from the window
        choice, values = mainmenuWindow.read()

        # Handle button clicks based on the user's selection
        if choice == 'Strength':
            mainmenuWindow.close()
            strength()  # Open the strength training window
        elif choice == 'Cardio':
            mainmenuWindow.close()
            cardio()  # Open the cardio workout window
        elif choice == 'Meditation':
            mainmenuWindow.close()
            meditation()
        elif choice == 'Meditation':
            """
            This option closes the main menu window and opens the meditation window.
            """
            mainmenuWindow.close()
            meditation()  # Open the meditation functionality

        elif choice in ('Exit', sg.WIN_CLOSED):
            """
            Handles both explicit 'Exit' button click and window close event.
            Closes the main menu window and terminates the program.
            """
            mainmenuWindow.close()
            exit()

        elif choice == 'Add Entry':
            """
            This option allows users to add a new weight entry.
            It hides the main menu window, prompts the user for their current weight,
            validates the input, and creates a new entry dictionary if valid.
            Finally, it calls the `add_entry` function to save the new entry to the file.
            """
            mainmenuWindow['-OUTPUT-'].update('')  # Clear output text
            mainmenuWindow.hide()

            entry1 = sg.PopupGetText('Current Weight: ')

            # Validate weight input
            if entry1 is None or not entry1.replace('.', '', 1).isdigit():
                mainmenuWindow.un_hide()  # Show window again if input is invalid
            else:
                entry = {
                    'number': next_entry_number,  # Assign next available ID
                    'weight': entry1,
                    'date': datetime.today().strftime('%m-%d-%Y')  # Use current date
                }
                add_entry(mainmenuWindow, weightList, weightFile, entry)

        elif choice == 'Delete Entry':
            """
            This option allows users to delete an existing weight entry.
            It clears the output text, calls the `delete_entry` function to handle deletion,
            and updates the weight list and file accordingly.
            """
            mainmenuWindow['-OUTPUT-'].update('')
            delete_entry(mainmenuWindow, weightList, weightFile)




# Menus and fonts using PySimpleGUI
buttonFont = ('Courier', 23)
titleFont = ('Courier', 30)
textFont = ('Arial Italic', 11)

def open_mainmenu():
    global mainmenuWindow
    # Main Menu
    TitleCol = [
        [sg.Text(f'7 Day Average: \nLast 14 Days: ', key='WEEKLY', justification='center', font=textFont), sg.Push(), sg.Text(f'Weight', justification='center', font=titleFont), sg.Push()]
    ]
    LineCol = [
        [sg.Multiline(size=(80, 30), key='-OUTPUT-', background_color='black', text_color='white', disabled=True, autoscroll=True, font=textFont),sg.Canvas(size=(400, 400), key='-CANVAS-')]
    ]


    mainmenuLayout = [
        [sg.Column(TitleCol, element_justification='center', expand_x=True)],
        [sg.Column(LineCol, element_justification='left', expand_x=True)],
        [sg.Button('Exit', font=buttonFont), sg.Push(),sg.Button('Strength', font=buttonFont),sg.Button('Cardio', font=buttonFont),sg.Button('Meditation', font=buttonFont), sg.Push(), sg.Button('Add Entry', font=buttonFont), sg.Button('Delete Entry', font=buttonFont)]
        ]
    mainmenuWindow = sg.Window(title=windowTitle, layout=mainmenuLayout, margins=(80,75), use_custom_titlebar=True, finalize=True, keep_on_top=True, titlebar_icon=titlebarIcon)



def open_strength():
    global strengthWindow
    TitleCol = [
        [sg.Text(f'7 Day Average: \nLast 14 Days: ', key='WEEKLY', justification='center', font=textFont), sg.OptionMenu(values=[1], key='OPTIONS', default_value='Test'), sg.Button('Update'), sg.Push(), sg.Text(f'Strength', justification='center', font=titleFont), sg.Push()]
    ]
    LineCol = [
        [sg.Multiline(size=(80, 30), key='-OUTPUT-', background_color='black', text_color='white', disabled=True, autoscroll=True, font=textFont),sg.Canvas(size=(400, 400), key='-CANVAS-')]
    ]

    
    Layout = [
        [sg.Column(TitleCol, element_justification='center', expand_x=True)],
        [sg.Column(LineCol, element_justification='left', expand_x=True)],
        [sg.Button('Exit', font=buttonFont), sg.Push(),sg.Button('Weight', font=buttonFont),sg.Button('Cardio', font=buttonFont),sg.Button('Meditation', font=buttonFont), sg.Push(), sg.Button('Add Entry', font=buttonFont), sg.Button('Delete Entry', font=buttonFont)]
        ]
    
 



    strengthWindow = sg.Window(title=windowTitle, layout=Layout, margins=(15,75), use_custom_titlebar=True, finalize=True, keep_on_top=True, titlebar_icon=titlebarIcon)

def open_cardio():
    global cardioWindow
    TitleCol = [
        [sg.Text(f'7 Day Average: \nLast 14 Days: ', key='WEEKLY', justification='center', font=textFont), sg.Push(), sg.Text(f'Cardio', justification='center', font=titleFont), sg.Push()]
    ]
    LineCol = [
        [sg.Multiline(size=(80, 30), key='-OUTPUT-', background_color='black', text_color='white', disabled=True, autoscroll=True, font=textFont),sg.Canvas(size=(400, 400), key='-CANVAS-')]
    ]

    Layout = [
        [sg.Column(TitleCol, element_justification='center', expand_x=True)],
        [sg.Column(LineCol, element_justification='left', expand_x=True)],
        [sg.Button('Exit', font=buttonFont), sg.Push(),sg.Button('Strength', font=buttonFont),sg.Button('Weight', font=buttonFont),sg.Button('Meditation', font=buttonFont), sg.Push(), sg.Button('Add Entry', font=buttonFont), sg.Button('Delete Entry', font=buttonFont)]
        ]
    cardioWindow = sg.Window(title=windowTitle, layout=Layout, margins=(15,75), use_custom_titlebar=True, finalize=True, keep_on_top=True, titlebar_icon=titlebarIcon)

def open_meditation():
    global meditationWindow
    TitleCol = [
        [sg.Text(f'7 Day Average: \nLast 14 Days: ', key='WEEKLY', justification='center', font=textFont), sg.Push(), sg.Text(f'Meditation', justification='center', font=titleFont), sg.Push()]
    ]
    LineCol = [
        [sg.Multiline(size=(80, 30), key='-OUTPUT-', background_color='black', text_color='white', disabled=True, autoscroll=True, font=textFont),sg.Canvas(size=(400, 400), key='-CANVAS-')]
    ]

    Layout = [
        [sg.Column(TitleCol, element_justification='center', expand_x=True)],
        [sg.Column(LineCol, element_justification='left', expand_x=True)],
        [sg.Button('Exit', font=buttonFont), sg.Push(),sg.Button('Strength', font=buttonFont),sg.Button('Cardio', font=buttonFont),sg.Button('Weight', font=buttonFont), sg.Push(), sg.Button('Add Entry', font=buttonFont), sg.Button('Delete Entry', font=buttonFont)]
        ]
    meditationWindow = sg.Window(title=windowTitle, layout=Layout, margins=(15,75), use_custom_titlebar=True, finalize=True, keep_on_top=True, titlebar_icon=titlebarIcon)



# Run Code
def main():
    while True:
        main_menu()

main()