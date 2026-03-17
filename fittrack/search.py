from fittrack import models as m

def run_query(query):
    result_list = []

    pages = m.Page.objects.filter(title__icontains=query)

    for page in pages:
        result_list.append({
            'title': page.title,
            'link': page.url,
            'summary': f"Views: {page.views}"
        })

    return result_list