#!/usr/bin/env python3
"""
LinkVault - URL Shortener with Analytics
A SaaS-style link management tool
"""

import os
import string
import random
from datetime import datetime, timedelta
from urllib.parse import urlparse
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///linkvault.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["BASE_URL"] = os.environ.get("BASE_URL", "http://localhost:5003")

db = SQLAlchemy(app)


# Models
class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(2048), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    title = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    clicks = db.relationship("Click", backref="link", lazy=True, cascade="all, delete-orphan")

    @property
    def total_clicks(self):
        return len(self.clicks)

    @property
    def short_url(self):
        return f"{app.config['BASE_URL']}/r/{self.short_code}"

    @property
    def domain(self):
        parsed = urlparse(self.original_url)
        return parsed.netloc

    @property
    def is_expired(self):
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False

    def clicks_last_days(self, days=7):
        cutoff = datetime.utcnow() - timedelta(days=days)
        return [c for c in self.clicks if c.clicked_at >= cutoff]


class Click(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey("link.id"), nullable=False)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    referrer = db.Column(db.String(500))
    country = db.Column(db.String(100))
    device_type = db.Column(db.String(50))
    browser = db.Column(db.String(50))


# Utility functions
def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        code = "".join(random.choices(chars, k=length))
        if not Link.query.filter_by(short_code=code).first():
            return code


def parse_user_agent(ua_string):
    try:
        from user_agents import parse

        ua = parse(ua_string)
        device = "mobile" if ua.is_mobile else "tablet" if ua.is_tablet else "desktop"
        browser = ua.browser.family
        return device, browser
    except Exception:
        return "unknown", "unknown"


# Routes
@app.route("/")
def dashboard():
    links = Link.query.order_by(Link.created_at.desc()).all()

    # Calculate stats
    total_links = len(links)
    total_clicks = sum(link.total_clicks for link in links)
    active_links = len([l for l in links if l.is_active and not l.is_expired])

    # Clicks over last 7 days for chart
    clicks_by_day = {}
    for i in range(7):
        day = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        clicks_by_day[day] = 0

    for link in links:
        for click in link.clicks_last_days(7):
            day = click.clicked_at.strftime("%Y-%m-%d")
            if day in clicks_by_day:
                clicks_by_day[day] += 1

    chart_data = [{"date": k, "clicks": v} for k, v in sorted(clicks_by_day.items())]

    return render_template(
        "dashboard.html",
        links=links[:10],
        total_links=total_links,
        total_clicks=total_clicks,
        active_links=active_links,
        chart_data=chart_data,
    )


@app.route("/links")
def all_links():
    links = Link.query.order_by(Link.created_at.desc()).all()
    return render_template("links.html", links=links)


@app.route("/link/<int:link_id>")
def link_detail(link_id):
    link = Link.query.get_or_404(link_id)

    # Click stats
    clicks_by_day = {}
    for i in range(30):
        day = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        clicks_by_day[day] = 0

    for click in link.clicks:
        day = click.clicked_at.strftime("%Y-%m-%d")
        if day in clicks_by_day:
            clicks_by_day[day] += 1

    chart_data = [{"date": k, "clicks": v} for k, v in sorted(clicks_by_day.items())]

    # Device breakdown
    devices = {}
    browsers = {}
    referrers = {}

    for click in link.clicks:
        devices[click.device_type or "unknown"] = devices.get(click.device_type or "unknown", 0) + 1
        browsers[click.browser or "unknown"] = browsers.get(click.browser or "unknown", 0) + 1
        ref = click.referrer or "Direct"
        if ref != "Direct":
            ref = urlparse(ref).netloc or "Direct"
        referrers[ref] = referrers.get(ref, 0) + 1

    return render_template(
        "link_detail.html",
        link=link,
        chart_data=chart_data,
        devices=devices,
        browsers=browsers,
        referrers=referrers,
    )


@app.route("/r/<short_code>")
def redirect_link(short_code):
    link = Link.query.filter_by(short_code=short_code).first_or_404()

    if not link.is_active or link.is_expired:
        return render_template("expired.html"), 410

    # Record click
    ua_string = request.headers.get("User-Agent", "")
    device, browser = parse_user_agent(ua_string)

    click = Click(
        link_id=link.id,
        ip_address=request.remote_addr,
        user_agent=ua_string[:500],
        referrer=request.referrer,
        device_type=device,
        browser=browser,
    )
    db.session.add(click)
    db.session.commit()

    return redirect(link.original_url)


@app.route("/api/link", methods=["POST"])
def create_link():
    data = request.get_json()

    if not data or not data.get("url"):
        return jsonify({"error": "URL is required"}), 400

    url = data["url"]
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # Validate URL
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return jsonify({"error": "Invalid URL"}), 400
    except Exception:
        return jsonify({"error": "Invalid URL"}), 400

    # Create link
    expires_at = None
    if data.get("expires_in_days"):
        expires_at = datetime.utcnow() + timedelta(days=int(data["expires_in_days"]))

    link = Link(
        original_url=url,
        short_code=data.get("custom_code") or generate_short_code(),
        title=data.get("title"),
        expires_at=expires_at,
    )

    try:
        db.session.add(link)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Short code already exists"}), 409

    return jsonify(
        {
            "success": True,
            "link": {
                "id": link.id,
                "short_url": link.short_url,
                "short_code": link.short_code,
                "original_url": link.original_url,
            },
        }
    )


@app.route("/api/link/<int:link_id>", methods=["PUT"])
def update_link(link_id):
    link = Link.query.get_or_404(link_id)
    data = request.get_json()

    if "title" in data:
        link.title = data["title"]
    if "is_active" in data:
        link.is_active = data["is_active"]

    db.session.commit()
    return jsonify({"success": True})


@app.route("/api/link/<int:link_id>", methods=["DELETE"])
def delete_link(link_id):
    link = Link.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()
    return jsonify({"success": True})


@app.route("/api/stats")
def api_stats():
    links = Link.query.all()
    return jsonify(
        {
            "total_links": len(links),
            "total_clicks": sum(l.total_clicks for l in links),
            "active_links": len([l for l in links if l.is_active and not l.is_expired]),
        }
    )


@app.route("/seed")
def seed_demo_data():
    """Seed with demo data for showcase."""
    Click.query.delete()
    Link.query.delete()

    # Create sample links
    demo_links = [
        {"url": "https://github.com/bradleycooke", "title": "GitHub Profile", "code": "github"},
        {"url": "https://linkedin.com/in/bradleycooke", "title": "LinkedIn", "code": "linkedin"},
        {"url": "https://example.com/product-launch", "title": "Product Launch Page", "code": "launch"},
        {"url": "https://docs.example.com/api", "title": "API Documentation", "code": "apidocs"},
        {"url": "https://blog.example.com/announcement", "title": "Blog Announcement", "code": "news"},
    ]

    devices = ["desktop", "mobile", "tablet"]
    browsers = ["Chrome", "Safari", "Firefox", "Edge"]
    referrers = ["https://twitter.com", "https://google.com", "https://linkedin.com", None, None]

    for data in demo_links:
        link = Link(
            original_url=data["url"],
            short_code=data["code"],
            title=data["title"],
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
        )
        db.session.add(link)
        db.session.flush()

        # Add random clicks
        num_clicks = random.randint(10, 100)
        for _ in range(num_clicks):
            click = Click(
                link_id=link.id,
                clicked_at=datetime.utcnow() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23)),
                device_type=random.choice(devices),
                browser=random.choice(browsers),
                referrer=random.choice(referrers),
            )
            db.session.add(click)

    db.session.commit()
    return redirect(url_for("dashboard"))


# Initialize database
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  LinkVault - URL Shortener")
    print("=" * 50)
    print("\n  Starting server at: http://localhost:5003")
    print("  Press Ctrl+C to stop\n")
    app.run(debug=True, port=5003)
