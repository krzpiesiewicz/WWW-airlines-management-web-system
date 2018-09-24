from django.conf.locale import id
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template import loader

from datetime import timedelta, datetime
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from linie_lotnicze.forms import TicketForm
from linie_lotnicze.models import Flight, Ticket, Crew, PilotInCommand, CrewMember


def main(request):
    return redirect('flights/1/100/')

def flights(request, row_no : int, rows_cnt : int):

    id = request.GET.get('id')
    flight_not_found = False
    if id != None:
        try:
            id = int(id)
            if Flight.objects.filter(id=id).exists():
                return redirect("/flight/%d/" % id)
            else:
                flight_not_found = True
        except:
            pass

    min_date_txt = request.GET.get('min_date')
    max_date_txt = request.GET.get('max_date')

    min_date = max_date = None

    if min_date_txt != None:
        min_date = parse_date(min_date_txt)
    if max_date_txt != None:
        max_date = parse_date(max_date_txt)

    if max_date is not None:
        max_date_plus_1 = max_date + timedelta(days=1)

    if (min_date != None and max_date != None):
        if min_date > max_date:
            max_date = min_date
            max_date_plus_1 = min_date + timedelta(days=1)
            max_date_txt = min_date_txt
        all_flights = Flight.objects.filter(start_time__range=[min_date, max_date_plus_1])
    elif min_date != None:
        all_flights = Flight.objects.filter(start_time__range=[min_date, datetime.max])
    elif max_date != None:
        all_flights = Flight.objects.filter(start_time__range=[datetime.min, max_date_plus_1])
    else:
        all_flights = Flight.objects.all()

    all_flights_cnt = all_flights.count()
    to_redirect = False
    if (rows_cnt < 1):
        rows_cnt = 100
    if (row_no < 1):
        row_no = 1
        to_redirect = True
    if (row_no > all_flights_cnt):
        row_no = all_flights_cnt - rows_cnt
        to_redirect = True
    if to_redirect:
        return redirect("/flights/%d/%d/" % (row_no, rows_cnt))

    flights = all_flights[row_no - 1:row_no - 1 + rows_cnt]

    next_page_link = "/flights/%d/%d/" % (max(1, min(all_flights_cnt - rows_cnt, row_no + rows_cnt)), rows_cnt)
    prev_page_link = "/flights/%d/%d/" % (max(1, row_no - rows_cnt), rows_cnt)

    return render(request, 'flights.html', locals())

def flight(request, id : Flight.id):
    flight = Flight.objects.get(id=id)
    free_seats = flight.free_seats()
    if free_seats == 0:
        no_seats = True

    if request.user.is_authenticated:
        if request.method == 'POST':
            ticket = Ticket(flight=flight)
            addTicketForm = TicketForm(request.POST, instance=ticket)
            addTicketForm.full_clean()
            if addTicketForm.is_valid():
                ticket = addTicketForm.save(commit=False)
                with transaction.atomic():
                    ticket.clean()
                    ticket.save()
                return redirect('flight', id)
        else:
            addTicketForm = TicketForm()

    passengers_tmp = Ticket.objects.filter(flight=flight).values_list('passenger')
    passengers = []
    for p in passengers_tmp:
        (val,) = p
        if (val not in passengers):
            passengers.append(val)

    return render(request, 'flight.html', locals())

def error404(request):
    return HttpResponseNotFound(loader.get_template('404.html').render(), status=404)

def forbidden403(request):
    return HttpResponseForbidden(loader.get_template('403.html').render(), status=403)

def csrf_failure(request, reason=""):
    return forbidden403(request)

@require_POST
@csrf_exempt
def login(request):
    if authenticate(username=request.POST['username'], password=request.POST['password']) is not None:
        return HttpResponse()
    else:
        return HttpResponseForbidden()

@require_POST
@csrf_exempt
def crews(request):
    if authenticate(username=request.POST['username'], password=request.POST['password']) is None:
        return HttpResponseForbidden()
    else:
        crews_set = Crew.objects.values('id', 'pilot_in_command__first_names', 'pilot_in_command__last_name')
        dic = {}
        for c in crews_set:
            key = c['id']
            dic[key] = {'pilot_firstnames': c['pilot_in_command__first_names'],
                   'pilot_lastname': c['pilot_in_command__last_name']}
        return JsonResponse({'crews': dic})

@require_POST
@csrf_exempt
def save_crew(request):
    if authenticate(username=request.POST['username'], password=request.POST['password']) is None:
        return HttpResponseForbidden()
    else:
        try:
            id = request.POST['crew_id']
            if id == "add-new":
                with transaction.atomic():
                    p = PilotInCommand(first_names=request.POST['pilot_firstnames'], last_name=request.POST['pilot_lastname'])
                    p.clean()
                    p.save()
                    c = Crew(pilot_in_command=p)
                    c.clean()
                    c.save()
                    return JsonResponse({'crew_id': c.id})

            else:
                id = int(id)
                c = Crew.objects.get(id=id)
                p = c.pilot_in_command
                p.first_names = request.POST['pilot_firstnames']
                p.last_name = request.POST['pilot_lastname']
                p.clean()
                p.save()
                return JsonResponse({'crew_id': c.id})
        except:
            return HttpResponseForbidden()

@require_POST
@csrf_exempt
def delete_crew(request):
    if authenticate(username=request.POST['username'], password=request.POST['password']) is None:
        return HttpResponseForbidden()
    else:
        try:
            id = int(request.POST['crew_id_to_del'])
            c = Crew.objects.get(id=id)
            c.delete()
            return HttpResponse()
        except:
            return HttpResponseForbidden()

@require_POST
@csrf_exempt
def crew_members(request):
    if authenticate(username=request.POST['username'], password=request.POST['password']) is None:
        return HttpResponseForbidden()
    else:
        try:
            crew_id = int(request.POST['crew_id'])
            members = CrewMember.objects.filter(crew=crew_id)
            dic = {}
            for m in members:
                dic[m.id] = {'firstnames': m.first_names, 'lastname': m.last_name}
            return JsonResponse({'members': dic})
        except:
            return HttpResponseForbidden()

@require_POST
@csrf_exempt
def save_member(request):
    if authenticate(username=request.POST['username'], password=request.POST['password']) is None:
        return HttpResponseForbidden()
    else:
        try:
            crew_id = request.POST['crew_id']
            member_id = request.POST['member_id']
            if member_id == "add-new":
                with transaction.atomic():
                    c = Crew.objects.get(id=crew_id)
                    m = CrewMember(first_names=request.POST['member_firstnames'],
                                   last_name=request.POST['member_lastname'],
                                   crew_id=crew_id)
                    m.clean()
                    m.save()
                    return JsonResponse({'id': m.id})
            else:
                with transaction.atomic():
                    member_id = int(member_id)
                    m = CrewMember.objects.get(id=member_id)
                    if (crew_id == m.crew_id):
                        raise ValidationError("Bad request data")
                    m.first_names = request.POST['member_firstnames']
                    m.last_name = request.POST['member_lastname']
                    m.clean()
                    m.save()
                    return JsonResponse({'crew_id': m.id})
        except:
            return HttpResponseForbidden()

@require_POST
@csrf_exempt
def delete_member(request):
    if authenticate(username=request.POST['username'], password=request.POST['password']) is None:
        return HttpResponseForbidden()
    else:
        try:
            member_id = request.POST['member_id_to_del']
            member_id = int(member_id)
            m = CrewMember.objects.get(id=member_id)
            m.delete()
            return HttpResponse()
        except:
            return HttpResponseForbidden()

@require_GET
def flights_ids(request, rows_cnt : int):
    try:
        middle_id = int(request.GET['flight_middle_id'])
        r_flights = Flight.objects.filter(Q(id__gte=middle_id))
        l_flights = Flight.objects.filter(Q(id__lt=middle_id))
        r_last = r_flights.count()
        l_last = l_flights.count()

        if (rows_cnt < 1):
            rows_cnt = 100
        r_flights = r_flights[0: min(r_last, (rows_cnt - 1) / 2)]
        l_flights = l_flights[max(0, l_last - (rows_cnt - 1) / 2) : l_last]
        list = []
        for f in l_flights:
            list.append(f.id)
        for f in r_flights:
            list.append(f.id)
        return JsonResponse({'flights': list})
    except:
        return HttpResponseForbidden

@require_POST
@csrf_exempt
def flight_crew(request):
    if authenticate(username=request.POST['username'], password=request.POST['password']) is None:
        return HttpResponseForbidden()
    else:
        try:
            flight_id = int(request.POST['flight_id'])
            f = Flight.objects.get(id=flight_id)
            crew_id = f.crew_id;
            if crew_id != None:
                return JsonResponse({'flight_crew_id': crew_id})
            else:
                return JsonResponse({})
        except:
            return HttpResponseForbidden()

@require_POST
@csrf_exempt
def save_flight(request):
    if authenticate(username=request.POST['username'], password=request.POST['password']) is None:
        return HttpResponseForbidden()
    else:
        try:
            crew_id = int(request.POST['crew_id'])
            flight_id = int(request.POST['flight_id'])
            f = Flight.objects.get(id=flight_id)
            c = Crew.objects.get(id=crew_id)
            f.crew = c
            f.clean()
            f.save()
            return JsonResponse({'flight_crew_id': c.id})
        except ValidationError as e:
            return HttpResponseForbidden(e.message)