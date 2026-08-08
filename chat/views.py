import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Message

@login_required(login_url='login')
def get_chat_history(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    messages = Message.objects.filter(
        (Q(sender=request.user, receiver=other_user) |
         Q(sender=other_user, receiver=request.user))
    ).order_by('created_at')

    messages_data = [
        {
            'id': msg.id,
            'sender_id': msg.sender_id,
            'receiver_id': msg.receiver_id,
            'sender_username': msg.sender.username,
            'content': msg.content,
            'is_read': msg.is_read,
            'timestamp': msg.created_at.strftime('%b %d, %I:%M %p'),
            'is_me': msg.sender_id == request.user.id
        }
        for msg in messages
    ]

    return JsonResponse({'messages': messages_data})


@login_required(login_url='login')
def send_message(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON format.'}, status=400)

    receiver_id = data.get('receiver_id')
    content = data.get('content', '').strip()

    if not receiver_id:
        return JsonResponse({'success': False, 'error': 'Receiver ID is required.'}, status=400)

    if not content:
        return JsonResponse({'success': False, 'error': 'Message content cannot be empty.'}, status=400)

    receiver = get_object_or_404(User, id=receiver_id)

    msg = Message.objects.create(
        sender=request.user,
        receiver=receiver,
        content=content
    )

    return JsonResponse({
        'success': True,
        'message': {
            'id': msg.id,
            'content': msg.content,
            'timestamp': msg.created_at.strftime('%b %d, %I:%M %p'),
            'is_me': True,
            'is_read': False
        }
    })


@login_required(login_url='login')
def mark_messages_as_read(request, other_user_id):
    """
    Marks all incoming unread messages sent by `other_user_id` to request.user as read.
    Broadcasts real-time read receipt event to `other_user_id` via Channel Layer.
    """
    if request.method not in ['PATCH', 'POST']:
        return JsonResponse({'success': False, 'error': 'Method not allowed.'}, status=405)

    other_user = get_object_or_404(User, id=other_user_id)

    unread_messages = Message.objects.filter(
        sender=other_user,
        receiver=request.user,
        is_read=False
    )

    updated_count = unread_messages.update(is_read=True)

    if updated_count > 0:
        # Notify sender (other_user) in real time that their messages were read
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{other_user.id}",
            {
                'type': 'messages_read',
                'reader_id': request.user.id
            }
        )

    return JsonResponse({
        'success': True,
        'updated_count': updated_count,
        'message': f"{updated_count} messages marked as read."
    })


@login_required(login_url='login')
def get_users_list(request):
    users = User.objects.exclude(id=request.user.id).annotate(
        unread_count=Count(
            'sent_messages',
            filter=Q(sent_messages__receiver=request.user, sent_messages__is_read=False)
        )
    ).order_by('username')

    users_data = [
        {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'unread_count': user.unread_count
        }
        for user in users
    ]

    return JsonResponse({'users': users_data})
