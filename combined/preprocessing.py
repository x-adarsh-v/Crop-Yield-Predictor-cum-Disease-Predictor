import pandas as pd

def preprocess_input(data_dict, model_loader):
    """
    Transforms a dictionary of user input into a format suitable for the
    yield prediction model.

    Args:
        data_dict (dict): A dictionary containing the raw form data.
        model_loader (ModelLoader): The instance of the model loader class.

    Returns:
        pd.DataFrame: A DataFrame with the preprocessed features.
    """
    # Create a DataFrame from the input dictionary
    df = pd.DataFrame([data_dict])

    # Apply the pre-fitted label encoders to categorical columns
    df['Region'] = model_loader.le_region.transform(df['Region'])
    df['Soil_Type'] = model_loader.le_soil.transform(df['Soil_Type'])
    df['Crop'] = model_loader.le_crop.transform(df['Crop'])
    df['Weather_Condition'] = model_loader.le_weather.transform(df['Weather_Condition'])
    
    # Manually map binary ('Yes'/'No') features to 1/0
    df['Irrigation_Used'] = 1 if df['Irrigation_Used'].iloc[0] == 'Yes' else 0
    df['Fertilizer_Used'] = 1 if df['Fertilizer_Used'].iloc[0] == 'Yes' else 0
    
    # Scale numerical features using the pre-fitted scaler.
    # Note: The scaler was trained on [Rainfall, Temperature, Yield],
    # so we add a dummy '0' for the Yield column which will be ignored.
    scaled_values = model_loader.scaler.transform([
        [df['Rainfall_mm'].iloc[0], df['Temperature_Celsius'].iloc[0], 0]
    ])[0]
    
    # Update the DataFrame with the scaled values
    df['Rainfall_mm'] = scaled_values[0]
    df['Temperature_Celsius'] = scaled_values[1]
    
    # Return the final feature set in the correct order for the model
    return df[[
        'Region', 'Soil_Type', 'Crop', 'Rainfall_mm',
        'Temperature_Celsius', 'Fertilizer_Used',
        'Irrigation_Used', 'Weather_Condition'
    ]]
