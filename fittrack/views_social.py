import fittrack.models as m
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import redirect, render


@login_required
def friends(request):
    current_user = request.user

    search_results = None
    if request.method == "POST":
        if "search_user" in request.POST:
            query = request.POST.get("search_user")
            existing = m.Friendship.objects.filter(
                Q(user_a=current_user) | Q(user_b=current_user)
            ).values_list("user_a_id", "user_b_id")
            exclude_ids = {current_user.id}
            for a, b in existing:
                exclude_ids.add(a)
                exclude_ids.add(b)
            search_results = User.objects.filter(
                username__icontains=query
            ).exclude(id__in=exclude_ids)

        elif "add_friend" in request.POST:
            target_user = User.objects.get(id=request.POST.get("friend_id"))
            m.Friendship.objects.get_or_create(
                user_a=current_user, user_b=target_user, status=False
            )
            return redirect("fittrack:friends")

        elif "accept_friend" in request.POST:
            friendship = m.Friendship.objects.get(id=request.POST.get("request_id"))
            friendship.status = True
            friendship.save()
            return redirect("fittrack:friends")

    pending_requests = m.Friendship.objects.filter(
        user_b=current_user, status=False
    )

    friends_query = m.Friendship.objects.filter(
        (Q(user_a=current_user) | Q(user_b=current_user)) & Q(status=True)
    )
    confirmed_friends = []
    for f in friends_query:
        friend_obj = f.user_b if f.user_a == current_user else f.user_a
        recent = (
            m.WorkoutSession.objects.filter(user=friend_obj).order_by("-date").first()
        )
        confirmed_friends.append({"user": friend_obj, "recent": recent})

    context = {
        "pending_requests": pending_requests,
        "confirmed_friends": confirmed_friends,
        "search_results": search_results,
    }
    return render(request, "fittrack/friends.html", context)

