import time
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Payment
from instamojo_wrapper import Instamojo
from django.conf import settings

# Instamojo API client
api = Instamojo(
    api_key=settings.INSTAMOJO_API_KEY,
    auth_token=settings.INSTAMOJO_AUTH_TOKEN,
    endpoint=settings.INSTAMOJO_ENDPOINT,
)

def home(request):
    return HttpResponse("Welcome to the Instamojo Plugin!")  # Root view content

def payment_form(request):
    return render(request, 'instamojo_plugin/payment_form.html')  # Path relative to templates/

def create_payment_request(request):
    if request.method == 'POST':
        # Collecting payment details from the form
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        amount = request.POST.get('amount')

        # Ensure all required fields are provided
        if not all([name, email, phone, amount]):
            return HttpResponse("Missing required fields", status=400)

        # Generate a unique order ID
        ORDER_ID = 'ORD' + str(int(time.time()))

        # Prepare the parameters for the Instamojo payment request
        payment_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'amount': amount,
            'order_id': ORDER_ID,
            'currency': 'INR',  # Set the currency
            'redirect_url': 'http://127.0.0.1:8000/payment/callback/',  # Your payment callback URL
        }

        # Create a payment request using Instamojo API
        try:
            response = api.payment_request_create(
                purpose="Payment for order",
                name=name,
                amount=amount,
                buyer_name=name,
                email=email,
                phone=phone,
                redirect_url=payment_data['redirect_url'],
            )
            
            # Save payment details in database before redirecting
            payment = Payment(
                name=name,
                email=email,
                phone=phone,
                amount=amount,
                order_id=ORDER_ID,  
                status='initiated',  # Initial status
            )
            payment.save()

            # Prepare the form for Instamojo redirection
            pay_url = response['payment_request']['longurl']
            return render(request, 'payment_redirect.html', {'pay_url': pay_url})

        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)

    return HttpResponse("Invalid request", status=400)

@csrf_exempt
def payment_callback(request):
    """ Handle the callback from Instamojo after payment. """
    payment_id = request.GET.get('payment_id')
    payment_request_id = request.GET.get('payment_request_id')

    if payment_id and payment_request_id:
        # Fetch payment details from Instamojo
        try:
            response = api.payment_request_payment_status(
                payment_request_id=payment_request_id,
                payment_id=payment_id,
            )

            # Extract payment status from response
            payment_status = response['payment']['status']
            order_id = response['payment']['order_id']
            txn_id = response['payment']['payment_id']  # Use the payment_id as txn_id from Instamojo

            # Update the payment status in the database
            payment = Payment.objects.get(order_id=order_id)
            payment.status = payment_status
            payment.transaction_id = txn_id
            payment.save()

            # Return success or failure message
            if payment_status == 'Credit':
                return HttpResponse("Payment Successful")
            else:
                return HttpResponse("Payment Failed")

        except Payment.DoesNotExist:
            return HttpResponse("Invalid Order ID", status=400)
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)
    else:
        return HttpResponse("Missing payment_id or payment_request_id", status=400)

def transactions(request):
    """ Display all payment transactions (you can extend this view to list payment transactions). """
    payments = Payment.objects.all()
    return render(request, 'transactions.html', {'payments': payments})
