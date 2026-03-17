#!/bin/bash
# Run this in your project root: bash fix_login.sh

cat > templates/fittrack/login.html << 'ENDOFFILE'
{% extends 'fittrack/base.html' %}
{% load static %}

{% block title %}FitTrack - Login{% endblock %}

{% block extra_css %}
<style>
    .auth-wrapper {
        min-height: 100vh; display: flex; align-items: center; justify-content: center;
        padding: 2rem; position: relative;
    }
    .auth-wrapper::before {
        content: ''; position: fixed; inset: 0;
        background-image: linear-gradient(rgba(0,230,118,0.015) 1px, transparent 1px), linear-gradient(90deg, rgba(0,230,118,0.015) 1px, transparent 1px);
        background-size: 60px 60px; pointer-events: none;
    }
    .auth-card {
        width: 100%; max-width: 380px; position: relative; z-index: 1;
        background: #161616; border: 1px solid #262626; border-radius: 16px; overflow: hidden;
    }
    .auth-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, #00e676, transparent); }
    .auth-close {
        position: absolute; top: 1rem; right: 1rem; width: 32px; height: 32px; border-radius: 8px;
        background: rgba(255,255,255,0.04); border: 1px solid #2a2a2a;
        display: flex; align-items: center; justify-content: center;
        color: #666; text-decoration: none; transition: all 0.2s; font-size: 1rem; z-index: 2;
    }
    .auth-close:hover { background: rgba(255,255,255,0.08); color: #ccc; border-color: #444; }
    .auth-body { padding: 2rem; }
    .auth-brand { text-align: center; margin-bottom: 1.5rem; }
    .auth-brand a { font-family: 'Bebas Neue', sans-serif; font-size: 1.1rem; letter-spacing: 5px; color: #00e676; text-decoration: none; }
    .auth-title { text-align: center; font-size: 1.2rem; font-weight: 600; color: #f0f0f0; margin-bottom: 1.5rem; }
    .auth-label { display: block; font-size: 0.8rem; font-weight: 500; color: #888; margin-bottom: 0.35rem; }
    .auth-input {
        width: 100%; padding: 0.65rem 0.85rem; background: rgba(255,255,255,0.06);
        border: 1px solid #333; border-radius: 8px; color: #f0f0f0; font-size: 0.9rem;
        font-family: 'Outfit', sans-serif; transition: all 0.2s; box-sizing: border-box;
    }
    .auth-input::placeholder { color: #555; }
    .auth-input:focus { outline: none; border-color: #00e676; background: rgba(255,255,255,0.08); box-shadow: 0 0 0 3px rgba(0,230,118,0.1); }
    .auth-group { margin-bottom: 1rem; }
    .auth-submit {
        width: 100%; padding: 0.7rem; background: #00e676; color: #000; border: none;
        border-radius: 8px; font-weight: 600; font-size: 0.9rem; letter-spacing: 1px;
        cursor: pointer; font-family: 'Outfit', sans-serif; transition: all 0.2s; margin-top: 0.5rem;
    }
    .auth-submit:hover { background: #00c853; transform: translateY(-1px); }
    .auth-divider { border: none; border-top: 1px solid #262626; margin: 1.2rem 0; }
    .auth-footer { text-align: center; font-size: 0.85rem; color: #555; }
    .auth-footer a { color: #00e676; text-decoration: none; font-weight: 600; }
    .auth-footer a:hover { color: #00c853; }
    .auth-forgot { text-align: right; margin-top: -0.3rem; margin-bottom: 1rem; }
    .auth-forgot a { color: #555; font-size: 0.78rem; text-decoration: none; transition: color 0.2s; }
    .auth-forgot a:hover { color: #00e676; }
    .auth-error {
        background: rgba(255,82,82,0.08); border: 1px solid rgba(255,82,82,0.15);
        border-radius: 8px; padding: 0.5rem 0.8rem; color: #ff8a80; font-size: 0.83rem; margin-bottom: 1rem;
    }
</style>
{% endblock %}

{% block auth_content %}
<div class="auth-wrapper">
    <div class="auth-card">
        <a href="{% url 'fittrack:index' %}" class="auth-close" aria-label="Back to home"><i class="bi bi-x-lg"></i></a>
        <div class="auth-body">
            <div class="auth-brand"><a href="{% url 'fittrack:index' %}">FITTRACK</a></div>
            <div class="auth-title">Welcome back</div>

            {% if messages %}{% for message in messages %}
            <div class="auth-error">{{ message }}</div>
            {% endfor %}{% endif %}

            <form method="POST" action="{% url 'fittrack:login' %}">
                {% csrf_token %}
                <div class="auth-group">
                    <label class="auth-label" for="username">Username</label>
                    <input type="text" class="auth-input" id="username" name="username" placeholder="Enter your username" required autofocus>
                </div>
                <div class="auth-group">
                    <label class="auth-label" for="password">Password</label>
                    <input type="password" class="auth-input" id="password" name="password" placeholder="Enter your password" required>
                </div>
                <div class="auth-forgot">
                    <a href="{% url 'fittrack:forgot_password' %}">Forgot password?</a>
                </div>
                <button type="submit" class="auth-submit">LOGIN</button>
            </form>

            <hr class="auth-divider">
            <div class="auth-footer">Don't have an account? <a href="{% url 'fittrack:register' %}">Register</a></div>
        </div>
    </div>
</div>
{% endblock %}
ENDOFFILE

echo "login.html has been updated successfully!"
