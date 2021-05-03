from .models import Subscription
import stripe
from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from django.contrib.auth.models import User
from profiles.models import Profile
from django.conf import settings

def premium_required(function):
    def wrap(request, *args, **kwargs):
        if not request.user.profile.is_premium and settings.AUTO_PREMIUM_SUBSCRIPTION:
            print ('setting premium')
            current_profile = Profile.objects.get(user_id=request.user.id)
            current_profile.is_premium = False
            current_profile.save()
            return function(request, *args, **kwargs)

        if request.user.profile.is_premium:
            if not settings.AUTO_PREMIUM_SUBSCRIPTION:
                customer_stripe_id = Subscription.objects.filter(user_id=request.user).first()
                customer = stripe.Customer.retrieve(customer_stripe_id.customer_id)
                for sub in customer.subscriptions:
                    # If subscription is active or unpaid/cancelled but not yet inactive
                    if sub.status == 'active' or sub.status == 'trialing' or sub.status == 'incomplete' or sub.status == 'past_due' or sub.status == 'canceled':
                        return function(request, *args, **kwargs)
            
                current_profile = Profile.objects.get(user_id=request.user.id)
                current_profile.is_premium = False
                current_profile.save()
                return redirect(reverse('subscribe'))
            else:
                return function(request, *args, **kwargs)
        else:
            if request.is_ajax():
                data = {}
                data['redirect'] = '/subscribe'
                return JsonResponse(data)
            return redirect(reverse('subscribe'))
            
    return wrap
    

    
    