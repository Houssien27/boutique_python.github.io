"""
Boutique en ligne "Dar El Houssien" - version Python (Flask)
--------------------------------------------------------
Une petite boutique d'artisanat tunisien avec panier en session.

Pour lancer :
    pip install flask
    python app.py
Puis ouvrir : http://127.0.0.1:5000
"""

from flask import Flask, render_template, redirect, url_for, session, request, flash

app = Flask(__name__)
app.secret_key = "change-cette-cle-en-production"  # nécessaire pour utiliser la session

# --------------------------------------------------------------------
# "Base de données" des produits (ici en mémoire pour rester simple).
# Dans un vrai projet, ce serait une table SQL (voir commentaire plus bas).
# --------------------------------------------------------------------
PRODUCTS = [
    {"id": 1, "name": "Short Imprimé Monogramme", "tag": "Vêtement", "price": 300,
 "desc": "Short taille élastique, imprimé motif monogramme beige et bordeaux.",
 "emoji": "🩳", "image": "images/short-fleuri-tropical1.png"},
    {"id": 2, "name": "Creed Aventus 10ml", "tag": "Parfum", "price": 900,
     "desc": "Extrait de parfum en flacon vaporisateur, format voyage 10ml.",
     "emoji": "🧴", "image": "images/creed-aventus-10ml.jpg"},
    {"id": 3, "name": "Ensemble Pyjama Original", "tag": "Vêtement", "price": 550,
 "desc": "Ensemble chemise et short en tissu seersucker, taille M.",
 "emoji": "👔", "image": "images/ensemble-original-gris.jpg"},
     {"id": 4, "name": "Ensemble Original Kaki", "tag": "Vêtement", "price": 550,
     "desc": "Ensemble chemise et short en tissu seersucker, coloris kaki.",
     "emoji": "👔", "image": "images/ensemble-original-gris1.png"},
    # ⚠️ Prix d'exemple à remplacer par le vrai prix :
    {"id": 5, "name": "Chemise Original Grise", "tag": "Vêtement", "price": 550,
     "desc": "Ensemble chemise et short en tissu seersucker, coloris gris clair.",
     "emoji": "👕", "image": "images/ensemble-original-gris2.png"},
    # ⚠️ Prix d'exemple à remplacer par le vrai prix :
    {"id": 6, "name": "Short Fleuri Tropical", "tag": "Vêtement", "price": 300,
     "desc": "Short imprimé fleurs tropicales, taille élastique et cordon de serrage.",
     "emoji": "🩳", "image": "images/short-fleuri-tropical.png"},
]

# Numéro affiché pour le paiement (mobile money / Bankily / Masrvi, etc.)
# ⚠️ Remplace ce numéro d'exemple par ton vrai numéro.
PAYMENT_PHONE = "+222 32654783"

# Frais de livraison fixes, appliqués une seule fois par commande.
DELIVERY_FEE = 50

# --------------------------------------------------------------------
# Traduction (français / arabe) de tous les textes de l'interface.
# Les noms et descriptions des produits restent en français pour le
# moment (seule l'interface autour est traduite).
# --------------------------------------------------------------------
LANGUAGES = ["fr", "ar"]

TRANSLATIONS = {
    "fr": {
        "nav_products": "Produits",
        "nav_cart": "Panier",
        "hero_eyebrow": "Votre commerce de confiance",
        "hero_title": "Tout ce qu'il vous faut,<br>au même endroit.",
        "hero_text": "Un commerce général qui propose une sélection variée de produits "
                      "de qualité, pour toute la famille et tous les jours.",
        "hero_cta": "Voir tous les produits",
        "products_heading": "Nos produits",
        "products_sub": "{n} articles disponibles dans notre commerce.",
        "add_to_cart": "Ajouter",
        "footer_text": "Votre commerce de proximité. Démonstration Flask.",
        "cart_title": "Votre panier",
        "cart_empty": "Votre panier est vide.",
        "view_products": "Voir la collection",
        "per_unit": "/ unité",
        "remove": "Retirer",
        "subtotal": "Sous-total",
        "delivery": "Frais de livraison",
        "total": "Total",
        "payment_step1": "1. Transférez le montant via Bankily au numéro ci-dessous :",
        "payment_step2": "2. Envoyez la capture d'écran du transfert sur WhatsApp au même numéro,",
        "payment_step3": "ou passez directement à la boutique pour payer sur place.",
        "checkout": "Valider la commande",
    },
    "ar": {
        "nav_products": "المنتجات",
        "nav_cart": "السلة",
        "hero_eyebrow": "متجركم الموثوق",
        "hero_title": "كل ما تحتاجه،<br>في مكان واحد.",
        "hero_text": "متجر عام يقدم تشكيلة متنوعة من المنتجات الجيدة، لكل العائلة وكل يوم.",
        "hero_cta": "عرض جميع المنتجات",
        "products_heading": "منتجاتنا",
        "products_sub": "{n} منتج متوفر في متجرنا.",
        "add_to_cart": "أضف",
        "footer_text": "متجركم القريب. عرض تجريبي بتطبيق Flask.",
        "cart_title": "سلتك",
        "cart_empty": "سلتك فارغة.",
        "view_products": "شاهد المنتجات",
        "per_unit": "/ الوحدة",
        "remove": "إزالة",
        "subtotal": "المجموع الفرعي",
        "delivery": "رسوم التوصيل",
        "total": "المجموع",
        "payment_step1": "١. حوّل المبلغ عبر بنكيلي إلى الرقم أدناه:",
        "payment_step2": "٢. أرسل لقطة شاشة للتحويل عبر واتساب إلى نفس الرقم،",
        "payment_step3": "أو تعال مباشرة إلى المتجر للدفع في المكان.",
        "checkout": "تأكيد الطلب",
    },
}

# Traduction des catégories de produits (tag) uniquement.
TAG_TRANSLATIONS = {
    "ar": {
        "Livre": "كتاب",
        "Céramique": "خزف",
        "Bois": "خشب",
        "Fibre": "ألياف",
        "Textile": "نسيج",
        "Métal": "معدن",
        "Parfum": "عطر",
        "Vêtement": "ملابس",
    }
}


def get_lang():
    """Langue active pour le visiteur courant (par défaut : français)."""
    return session.get("lang", "fr")


@app.context_processor
def inject_i18n():
    """
    Rend disponibles dans TOUS les templates :
    - t(cle, **kwargs)   -> texte traduit de l'interface
    - tag(nom_categorie) -> nom de catégorie traduit
    - lang               -> code de langue actif ('fr' ou 'ar')
    - text_dir           -> 'rtl' pour l'arabe, 'ltr' pour le français
    """
    lang = get_lang()

    def t(key, **kwargs):
        text = TRANSLATIONS.get(lang, TRANSLATIONS["fr"]).get(key, key)
        return text.format(**kwargs) if kwargs else text

    def tag(tag_fr):
        return TAG_TRANSLATIONS.get(lang, {}).get(tag_fr, tag_fr)

    return dict(t=t, tag=tag, lang=lang, text_dir="rtl" if lang == "ar" else "ltr")


@app.route("/langue/<lang_code>")
def set_language(lang_code):
    """Change la langue de l'interface et revient à la page précédente."""
    if lang_code in LANGUAGES:
        session["lang"] = lang_code
    return redirect(request.referrer or url_for("index"))


def get_product(product_id):
    """Retourne le produit correspondant à l'id, ou None si absent."""
    for p in PRODUCTS:
        if p["id"] == product_id:
            return p
    return None


def get_cart_details():
    """
    Construit la liste détaillée du panier à partir de session['cart'],
    qui ne contient que { "1": quantite, "2": quantite, ... }.
    Retourne : (liste des articles, sous-total produits, frais de livraison, total).
    Les frais de livraison ne s'appliquent que si le panier n'est pas vide.
    """
    cart = session.get("cart", {})
    details = []
    subtotal = 0
    for pid_str, qty in cart.items():
        product = get_product(int(pid_str))
        if product:
            line_total = product["price"] * qty
            subtotal += line_total
            details.append({**product, "qty": qty, "line_total": line_total})

    delivery_fee = DELIVERY_FEE if details else 0
    total = subtotal + delivery_fee
    return details, subtotal, delivery_fee, total


# --------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------

@app.route("/")
def index():
    """Page d'accueil : liste des produits."""
    cart = session.get("cart", {})
    cart_count = sum(cart.values())
    return render_template("index.html", products=PRODUCTS, cart_count=cart_count)


@app.route("/ajouter/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    """Ajoute une unité du produit au panier (stocké dans la session)."""
    if not get_product(product_id):
        flash("Produit introuvable.")
        return redirect(url_for("index"))

    cart = session.get("cart", {})
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    session["cart"] = cart
    session.modified = True
    return redirect(url_for("index"))


@app.route("/panier")
def view_cart():
    """Affiche le contenu du panier avec le sous-total, les frais de livraison et le total."""
    details, subtotal, delivery_fee, total = get_cart_details()
    return render_template(
        "cart.html",
        items=details,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total=total,
        payment_phone=PAYMENT_PHONE,
    )


@app.route("/panier/augmenter/<int:product_id>", methods=["POST"])
def increase_qty(product_id):
    cart = session.get("cart", {})
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    session["cart"] = cart
    session.modified = True
    return redirect(url_for("view_cart"))


@app.route("/panier/diminuer/<int:product_id>", methods=["POST"])
def decrease_qty(product_id):
    cart = session.get("cart", {})
    key = str(product_id)
    if key in cart:
        cart[key] -= 1
        if cart[key] <= 0:
            del cart[key]
    session["cart"] = cart
    session.modified = True
    return redirect(url_for("view_cart"))


@app.route("/panier/retirer/<int:product_id>", methods=["POST"])
def remove_item(product_id):
    cart = session.get("cart", {})
    key = str(product_id)
    if key in cart:
        del cart[key]
    session["cart"] = cart
    session.modified = True
    return redirect(url_for("view_cart"))


@app.route("/commander", methods=["POST"])
def checkout():
    """Valide la commande (démonstration : pas de vrai paiement)."""
    details, subtotal, delivery_fee, total = get_cart_details()
    if not details:
        flash("Votre panier est vide.")
        return redirect(url_for("view_cart"))

    # Ici, dans un vrai projet, on enregistrerait la commande en base
    # de données et on redirigerait vers un vrai système de paiement
    # (Stripe, PayPal, etc.)
    session["cart"] = {}
    flash(f"Merci ! Commande validée pour un total de {total} UM "
          f"(dont {delivery_fee} UM de livraison). "
          f"Transférez le montant via Bankily au {PAYMENT_PHONE}, "
          f"puis envoyez la capture d'écran sur WhatsApp au même numéro, "
          f"ou passez directement à la boutique.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)