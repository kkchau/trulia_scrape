"""Feature parsing handlers







Dictionary keys are regular expression strings and the values are functions on how to



format the string. Each key will have to be iterated over to figure out which string



matches the query in question.



"""


feature_parser = {
    r"^Number of Bedrooms": lambda x: {
        "beds": int(x.replace("Number of Bedrooms: ", ""))
    },
    r"^Number of Bathrooms \(full\)": lambda x: {
        "baths_full": int(x.replace("Number of Bathrooms (full): ", ""))
    },
    r"^Number of Bathrooms \(half\)": lambda x: {
        "baths_half": int(x.replace("Number of Bathrooms (half): ", ""))
    },
    r"^Living Area": lambda x: {
        "living_area": float(x.replace("Living Area: ", "").replace(" Square Feet", ""))
    },
    r"^Lot Area": lambda x: {
        "lot_area": float(x.replace("Lot Area: ", "").replace(" Square Feet", ""))
    },
    r"Number of Garage Spaces": lambda x: {
        "garage_spaces": int(x.replace("Number of Garage Spaces: ", ""))
    },
    r"^Year Built": lambda x: {"year_built": int(x.replace("Year Built: ", ""))},
}
