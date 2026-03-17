from django.shortcuts import render, redirect
from django.db.models import Q
from fittrack.models import User, Friendship, WorkoutSession

def friends(request):
    # Integration Note: This gets the user from the session set by your teammate's login
    current_username = request.session.get('username') 
    if not current_username:
        return redirect('fittrack:index')
        
    try:
        current_user = User.objects.get(username=current_username)
    except User.DoesNotExist:
        return redirect('fittrack:index')

    # --- HANDLE POST ACTIONS (Add, Accept, Search) ---
    search_results = None
    if request.method == 'POST':
        # Action: Search for users
        if 'search_user' in request.POST:
            query = request.POST.get('search_user')
            # Exclude current user and people they are already in a friendship record with
            existing_friendships = Friendship.objects.filter(
                Q(userid_a=current_user) | Q(userid_b=current_user)
            ).values_list('userid_a_id', 'userid_b_id')
            
            # Flatten the ID list to exclude them from search
            exclude_ids = {current_user.id}
            for a, b in existing_friendships:
                exclude_ids.add(a)
                exclude_ids.add(b)
                
            search_results = User.objects.filter(
                username__icontains=query
            ).exclude(id__in=exclude_ids)

        # Action: Send Request
        elif 'add_friend' in request.POST:
            target_id = request.POST.get('friend_id')
            target_user = User.objects.get(id=target_id)
            Friendship.objects.get_or_create(
                userid_a=current_user, 
                userid_b=target_user, 
                status=False
            )
            return redirect('fittrack:friends')

        # Action: Accept Request
        elif 'accept_friend' in request.POST:
            req_id = request.POST.get('request_id')
            friendship = Friendship.objects.get(id=req_id)
            friendship.status = True
            friendship.save()
            return redirect('fittrack:friends')

    # --- PREPARE DISPLAY DATA ---
    # 1. Pending requests sent TO the user
    pending_requests = Friendship.objects.filter(userid_b=current_user, status=False)

    # 2. Confirmed Friends
    friends_query = Friendship.objects.filter(
        (Q(userid_a=current_user) | Q(userid_b=current_user)) & Q(status=True)
    )
    
    confirmed_friends = []
    for f in friends_query:
        # Determine which user in the pair is the 'other' person
        friend_obj = f.userid_b if f.userid_a == current_user else f.userid_a
        # Get their latest workout for the inspiration card
        recent_workout = WorkoutSession.objects.filter(userid=friend_obj).order_by('-date').first()
        confirmed_friends.append({
            'user': friend_obj,
            'recent': recent_workout
        })

    context_dict = {
        'pending_requests': pending_requests,
        'confirmed_friends': confirmed_friends,
        'search_results': search_results,
        'current_user': current_user,
    }
    return render(request, 'fittrack/friends.html', context=context_dict)
