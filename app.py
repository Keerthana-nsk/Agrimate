from flask import Flask, render_template, request, redirect, url_for, session
from xhtml2pdf import pisa
import random
import os
import requests
from werkzeug.utils import secure_filename
from flask import make_response
from io import BytesIO


app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_current_price(crop):
    url = f"https://api.farmonaut.com/prices/{crop}"
    res = requests.get(url, headers={'Authorization': 'Bearer YOUR_KEY'})
    if res.ok:
        return res.json()['price']
    return None

def predict_future_prices(current_price):
    return {
        'next_month': current_price * 1.05,
        'two_months': current_price * 1.08
    }


def predict_crop_price(crop_name):
    # Dummy prices for demo – replace with ML model later
    price_map = {
        'tea': 180,
        'tomato': 40,
        'coconut': 25,
        'mango': 60,
        'sweet_potato': 30,
        'ladies_finger': 45,
        'brinjal': 35,
        'greens': 20
    }
    return price_map.get(crop_name.lower(), random.randint(20, 100))

translations = {
    'en': {
        'login_title': "Login to Agrimate",
        'username': "Username",
        'email': "Email",
        'password': "Password",
        'login_btn': "Login",
        'no_account': "Don't have an account?",
        'signup': "Sign up here",
        'signup_title': "Create Your Account",
        'signup_btn': "Sign Up",
        'phone': "Phone Number",
        'login_instead': "Already have an account? Login",
        'land_title': 'Land Type Selection',
        'select_land_type': 'Select Your Land Type',
        'land_area': 'Land Area (Hectare/Cent):',
        'area_placeholder': 'e.g. 1 hectare or 50 cent',
        'upload_image': 'Upload a Picture of Your Land:',
        'click_land_type': 'Select the type of your land by clicking on an image:',
        'arable': 'Arable',
        'plantation': 'Plantation',
        'pastoral': 'Pastoral',
        'horticultural': 'Horticultural',
        'wetland': 'Wetland',
        'next': 'Next',
        'crop_status_title': "Crop Status",
        'choose_status': "Select your crop status:",
        'already_planted': "Already Planted",
        'going_to_plant': "Going to Plant",
        'next_btn': "Next",
        'season_title': "Select the Season",
        'choose_season': "Choose the current season",
        'summer': "Summer",
        'winter': "Winter",
        'spring': "Spring",
        'autumn': "Autumn",
        'crop_fertilizer_title': "Crop & Fertilizer Selection",
        'select_crop': "Select the crop you planted:",
        'select_fertilizer': "Select fertilizer type:",
        'growth': "Growth Fertilizer",
        'disease': "Disease Control Fertilizer",
        'tea': "Tea",
        'tomato': "Tomato",
        'coconut': "Coconut",
        'mango': "Mango",
        'sweet_potato': "Sweet Potato",
        'ladies_finger': "Ladies Finger",
        'brinjal': "Brinjal",
        'greens': "Greens",
        'planting_type_title': "Select Planting Type",
        'select_planting_type': "Choose the planting type:",
        'long_term': "Long-term Planting",
        'short_term': "Short-term Planting",
        'summary_title': "Your Agrimate Summary",
        'go_to_summary': "View Full Summary",
        'thank_you': "Thank you for using Agrimate!",
        'market_title': "Market Sales",
        'market_summary': "Market Price Summary",
        'crop': "Crop",
        'submit': "Submit",
        'next': "Next",
        'name': "Name",
        'predicted_price':"Predicted Price",
        '📊 Go to Market Sales':"📊 Go to Market Sales"
    },

    'ta': {
        'login_title': "அக்ரிமேட் உள்நுழைவு",
        'username': "பயனர் பெயர்",
        'email': "மின்னஞ்சல்",
        'password': "கடவுச்சொல்",
        'login_btn': "உள்நுழை",
        'no_account': "கணக்கு இல்லையா?",
        'signup': "இங்கே பதிவு செய்யவும்",
        'signup_title': "உங்கள் கணக்கை உருவாக்குங்கள்",
        'signup_btn': "பதிவு செய்யவும்",
        'phone': "தொலைபேசி எண்",
        'login_instead': "ஏற்கனவே கணக்கு உள்ளதா? உள்நுழையவும்",
        'land_title': 'நில வகை தேர்வு',
        'select_land_type': 'நிலத்தின் வகையைத் தேர்வுசெய்க',
        'land_area': 'நில பரப்பளவு (ஹெக்டேயர் / சென்ட்):',
        'area_placeholder': 'எ.கா. 1 ஹெக்டேயர் அல்லது 50 சென்ட்',
        'upload_image': 'நில புகைப்படத்தை பதிவேற்றுக:',
        'click_land_type': 'நில வகையை தேர்வு செய்ய படத்தை கிளிக் செய்க:',
        'arable': 'விவசாய நிலம்',
        'plantation': 'தோட்ட நிலம்',
        'pastoral': 'மாட்டு மேய்ச்சல் நிலம்',
        'horticultural': 'தோட்டக்கலை நிலம்',
        'wetland': 'ஈர நிலம்',
        'next': 'அடுத்தது',
        'crop_status_title': "விவசாய நிலை",
        'choose_status': "உங்கள் நிலையைத் தேர்வுசெய்க:",
        'already_planted': "ஏற்கனவே நட்டுவிட்டேன்",
        'going_to_plant': "நட்டுவைக்கப் போகிறேன்",
        'next_btn': "அடுத்தது",
        'season_title': "பருவத்தைத் தேர்வுசெய்க",
        'choose_season': "தற்போதைய பருவத்தை தேர்வுசெய்க",
        'summer': "கோடை",
        'winter': "குளிர்காலம்",
        'spring': "வசந்தகாலம்",
        'autumn': "இலையுதிர்காலம்",
        'crop_fertilizer_title': "விவசாய பயிர் மற்றும் உரம் தேர்வு",
        'select_crop': "நீங்கள் நடக்கப்பட்ட பயிரைத் தேர்வுசெய்க:",
        'select_fertilizer': "உர வகையைத் தேர்வுசெய்க:",
        'growth': "வளர்ச்சி உரம்",
        'disease': "நோய் தடுப்பு உரம்",
        'tea': "தேய்",
        'tomato': "தக்காளி",
        'coconut': "தேங்காய்",
        'mango': "மாம்பழம்",
        'sweet_potato': "இனிப்பு உருளைக்கிழங்கு",
        'ladies_finger': "வெண்டை",
        'brinjal': "கத்தரி",
        'greens': "கீரை",
        'planting_type_title': "நடவு வகையைத் தேர்வுசெய்க",
        'select_planting_type': "நடவு வகையைத் தேர்வுசெய்க:",
        'long_term': "நீண்டகால நடவு",
        'short_term': "குறுகியகால நடவு",
        'summary_title': "உங்கள் அக்ரிமேட் சுருக்கம்",
        'go_to_summary': "முழு சுருக்கத்தை காண்க",
        'thank_you': "அக்ரிமேட் பயன்படுத்தியதற்கு நன்றி!",
        'market_title': "சந்தை விற்பனை",
        'market_summary': "சந்தை விலை சுருக்கம்",
        'crop': "பயிர்",
        'submit': "சமர்ப்பிக்கவும்",
        'next': "அடுத்தது",
        'name':"பெயர்",
        'predicted_price':"கணிக்கப்பட்ட விலை",
        '📊 Go to Market Sales':"சந்தை விற்பனை பக்கம்"
    }
}
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/language', methods=['GET', 'POST'])
def language():
    if request.method == 'POST':
        selected_lang = request.form['language']
        if selected_lang in ['en','ta']:
            session['language'] = selected_lang
            return redirect(url_for('login'))  # 👈 Redirect to login page next

    return render_template('language.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    lang = session.get('language', 'en')
    trans = translations.get(lang, translations['en'])

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Store in session
        session['username'] = username
        session['email'] = email

        # Redirect to next step
        return redirect(url_for('land_measurement'))

    return render_template('login.html', trans=trans)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    lang = session.get('language', 'en')
    trans = translations.get(lang, translations['en'])

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        # You can store this in a file/database (Google Cloud later)
        session['username'] = username
        session['email'] = email
        session['phone'] = phone

        return redirect(url_for('login'))

    return render_template('signup.html', trans=trans)


@app.route('/land_measurement', methods=['GET', 'POST'])
def land_measurement():
    lang = session.get('language', 'en')
    trans = translations.get(lang, translations['en'])

    if request.method == 'POST':
        session['land_area'] = request.form['area']
        session['land_type'] = request.form['land_type']

        # Handle image upload
        land_image = request.files.get('land_image')
        if land_image:
            filename = secure_filename(land_image.filename)
            land_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            session['land_image'] = filename

        return redirect(url_for('crop_status'))

    return render_template('land_measurement.html', trans=trans)

@app.route('/crop_status', methods=['GET', 'POST'])
def crop_status():
    lang = session.get('language', 'en')
    trans = translations.get(lang, translations['en'])

    if request.method == 'POST':
        status = request.form['status']
        session['status'] = status

        return redirect(url_for('season_selection'))

    return render_template('crop_status.html', trans=trans)

@app.route('/season_selection', methods=['GET', 'POST'])
def season_selection():
    lang = session.get('language', 'en')
    trans = translations.get(lang, translations['en'])

    if request.method == 'POST':
        session['season'] = request.form['season']

        # Go to correct next step based on crop status
        if session.get('status') == 'planted':
            return redirect(url_for('planted_crop_selection'))
        else:
            return redirect(url_for('planting_type'))

    return render_template('season_selection.html', trans=trans)

@app.route('/planted_crop_selection', methods=['GET', 'POST'])
def planted_crop_selection():
    lang = session.get('language', 'en')
    trans = translations.get(lang, translations['en'])
    recommendation = ""

    if request.method == 'POST':
        crop = request.form['crop']
        fertilizer = request.form['fertilizer']

        session['crop'] = crop
        session['fertilizer'] = fertilizer

        # Basic recommendation logic
        if fertilizer == 'growth':
            recommendation = f"{trans[crop]}: Use NPK 20:20:20 for growth"
        elif fertilizer == 'disease':
            recommendation = f"{trans[crop]}: Use Neem or Bordeaux mix for disease control"

        return render_template('planted_crop_selection.html', trans=trans, recommendation=recommendation)

    return render_template('planted_crop_selection.html', trans=trans, recommendation=None)
@app.route('/planting_type', methods=['GET', 'POST'])
def planting_type():
    lang = session.get('language','en')
    trans = translations.get(lang, translations['en'])
    recommendation = ""

    if request.method == 'POST':
        planting_type = request.form['planting_type']
        session['planting_type'] = planting_type

        # Recommend crops
        if planting_type == 'long':
            crops = [trans['coconut'], trans['mango'], trans['tea']]
        else:
            crops = [trans['tomato'], trans['ladies_finger'], trans['greens'], trans['brinjal']]

        recommendation = f"{trans['select_planting_type']} {'/'.join(crops)}"

        return render_template('planting_type.html', trans=trans, recommendation=recommendation)

    return render_template('planting_type.html', trans=trans, recommendation=None)

@app.route('/market_sales')
def market_sales():
    lang = session.get('language', 'en')
    trans = translations.get(lang, translations['en'])

    crop = session.get('crop', '')
    if not crop:
        planting_type = session.get('planting_type', '')
        crop = 'mango' if planting_type == 'long' else 'tomato'

    predicted_price = predict_crop_price(crop)
    quantity = 1  # Optional: future input from user

    return render_template('market_sales.html', trans=trans, session=session, price=predicted_price)


@app.route('/download_summary')
def download_summary():
    lang = session.get('language', 'en')
    trans = translations.get(lang, translations['en'])

    crop = session.get('crop', '')
    if not crop:
        planting_type = session.get('planting_type', '')
        crop = 'mango' if planting_type == 'long' else 'tomato'

    predicted_price = predict_crop_price(crop)

    rendered_html = render_template('summary_pdf.html', trans=trans, session=session, price=predicted_price)

    # Convert HTML to PDF
    pdf_file = BytesIO()
    pisa_status = pisa.CreatePDF(rendered_html, dest=pdf_file)

    if pisa_status.err:
        return "Error generating PDF", 500

    response = make_response(pdf_file.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=agrimate_summary.pdf'
    response.headers['Content-Disposition'] = 'inline; filename=agrimate_summary.pdf'

    return response

if __name__ == '__main__':
    app.run(debug=True)