from django.shortcuts import get_object_or_404
from .models import CreditAquisition, Wallet
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
 
 
@receiver(valid_ipn_received)
def payment_notification(sender, **kwargs):
    ipn = sender
    if ipn.payment_status == 'Completed':
        # payment was successful
        credit_aquisition = get_object_or_404(CreditAquisition, id=ipn.invoice)
 
        if credit_aquisition.amount == ipn.mc_gross:
            # mark the order as paid
            credit_aquisition.status = 'A'
            # add credits to wallet
            wallet_obj = get_object_or_404(Wallet, user=credit_aquisition.user)
            wallet_obj.balance = wallet_obj.balance + credit_aquisition.amount
            # save obj
            credit_aquisition.save()
            wallet_obj.save()
        else:
            # mark the order as denied
            credit_aquisition.status = 'D'
            credit_aquisition.save()