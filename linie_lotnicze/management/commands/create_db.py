import string
import random
from datetime import timedelta
from math import floor
from typing import Union, Callable

from django.core.management.base import BaseCommand
import datetime
from datetime import datetime

from django.utils import timezone

from linie_lotnicze.models import *


class Command(BaseCommand):

    def handle(self, *args, **options):
        # self.create_airports()
        # self.create_planes()
        # self.create_crews()
        self.create_flights()
        # self.test()
        pass

    def test(self):
        t = Ticket(flight_id=1, number_of_seats=5)
        t.clean()
        t = Ticket.objects.get(id=2)
        t.clean()

    def create_airports(self):
        airports_names = ["Lotnisko Chopina w Warszawie", "Port lotniczy Kraków - Balice im. Jana Pawła II",
                          "Port lotniczy Gdańsk - Rębiechowo im. Lecha Wałęsy",
                          "Międzynarodowy Port Lotniczy Katowice w Pyrzowicach (KatowiceAirport)",
                          "Port lotniczy Warszawa - Modlin",
                          "Port lotniczy Wrocław - Strachowice im. Mikołaja Kopernika",
                          "Port lotniczy Poznań - Ławica im. Henryka Wieniawskiego", "Port lotniczy Rzeszów - Jasionka",
                          "Port lotniczy Szczecin - Goleniów im. NSZZ „Solidarność”", "Port lotniczy Lublin",
                          "Port Lotniczy im. Ignacego Jana Paderewskiego Bydgoszcz",
                          "Port lotniczy Łódź im. Władysława Reymonta", "Port lotniczy Olsztyn - Mazury",
                          "Port lotniczy Zielona Góra - Babimost", "Port lotniczy Radom - Sadków"]

        print("Airports:")
        for name in airports_names:
            a = Airport(name=name)
            print(a.name)
            a.save()

    def create_planes(self):
        prefixes = ["SN-L", "D-AAAA", "D-AZZZ", "G-EA", "N-"]
        print("Planes:")
        for i in range(60):
            random.seed(a=i)
            prefix = random.choice(prefixes)
            suffix = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
            p = Plane(code=prefix + suffix, seat_count=random.randrange(20, 70))
            print(p.code, p.seat_count)
            p.save()

    def create_crews(self):

        def generate_names(seed : int):

            first_names = ["Jan", "Stanisław", "Andrzej", "Józef", "Tadeusz", "Jerzy", "Zbigniew", "Krzysztof",
                           "Henryk",
                           "Ryszard", "Kazimierz", "Marek", "Marian", "Piotr", "Janusz", "Władysław", "Adam", "Wiesław",
                           "Zdzisław", "Edward", "Mieczysław", "Roman", "Mirosław", "Grzegorz", "Czesław", "Dariusz",
                           "Wojciech", "Jacek", "Eugeniusz", "Tomasz", "Stefan", "Zygmunt", "Leszek", "Bogdan",
                           "Antoni",
                           "Paweł", "Franciszek", "Sławomir", "Waldemar", "Jarosław", "Robert", "Mariusz",
                           "Włodzimierz",
                           "Michał", "Zenon", "Bogusław", "Witold", "Aleksander", "Bronisław", "Wacław", "Bolesław",
                           "Ireneusz", "Maciej", "Artur", "Edmund", "Marcin", "Lech", "Karol", "Rafał", "Arkadiusz",
                           "Leon",
                           "Sylwester", "Lucjan", "Julian", "Wiktor", "Romuald", "Bernard", "Ludwik", "Feliks",
                           "Alfred",
                           "Alojzy", "Przemysław", "Cezary", "Daniel", "Mikołaj", "Ignacy", "Lesław"]

            last_names = ["Nowak", "Kowalski", "Wiśniewski", "Wójcik", "Kowalczyk", "Kamiński", "Lewandowski",
                          "Dąbrowski",
                          "Zieliński", "Szymański", "Woźniak", "Kozłowski", "Jankowski", "Mazur", "Wojciechowski",
                          "Kwiatkowski", "Krawczyk", "Kaczmarek", "Piotrowski", "Grabowski", "Zając", "Pawłowski",
                          "Michalski", "Król", "Nowakowski", "Wieczorek", "Wróbel", "Jabłoński", "Dudek", "Adamczyk",
                          "Majewski", "Nowicki", "Olszewski", "Stępień", "Jaworski", "Malinowski", "Pawlak", "Górski",
                          "Witkowski", "Walczak", "Sikora", "Rutkowski", "Baran", "Michalak", "Szewczyk", "Ostrowski",
                          "Tomaszewski", "Pietrzak", "Duda", "Zalewski", "Wróblewski", "Jasiński", "Marciniak", "Bąk",
                          "Zawadzki", "Sadowski", "Jakubowski", "Wilk", "Włodarczyk", "Chmielewski", "Borkowski",
                          "Sokołowski", "Szczepański", "Sawicki", "Lis", "Kucharski", "Mazurek", "Kubiak", "Kalinowski",
                          "Wysocki", "Maciejewski", "Czarnecki", "Kołodziej", "Urbański", "Kaźmierczak", "Sobczak",
                          "Konieczny", "Głowacki", "Zakrzewski", "Krupa", "Wasilewski", "Krajewski", "Adamski",
                          "Sikorski",
                          "Mróz", "Laskowski", "Gajewski", "Ziółkowski", "Szulc", "Makowski", "Czerwiński",
                          "Baranowski",
                          "Szymczak", "Brzeziński", "Kaczmarczyk", "Przybylski", "Cieślak", "Borowski", "Błaszczyk",
                          "Andrzejewski"]

            names_num = random.choice([1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3])
            names = []
            for j in range(names_num):
                ok = False
                while (not ok):
                    name = first_names[random.randrange(0, len(first_names))];
                    if (name not in names):
                        names.append(name)
                        ok = True
            first_name = names[0];
            for j in range(1, names_num):
                first_name += " " + names[j]
            last_name = last_names[random.randrange(0, len(last_names))]

            return (first_name, last_name)

        for z in range(60):

            random.seed(a=2424 * z)

            (first_name, last_name) = generate_names(random.random)
            pilot_in_command = PilotInCommand(first_names=first_name, last_name=last_name)
            pilot_in_command.save()

            crew = Crew(pilot_in_command=pilot_in_command)
            crew.save()

            members_cnt = random.randrange(2, 5)
            for i in range(members_cnt):
                (first_name, last_name) = generate_names(random.random)
                member = CrewMember(first_names=first_name, last_name=last_name, crew=crew)
                member.save()

    def create_flights(self):

        random.seed(a=100)

        airport_count = Airport.objects.count()
        start_time_min_begin = datetime(2018, 5, 8)
        start_time_max_begin = datetime(2018, 5, 15)
        begin_duration = start_time_max_begin - start_time_min_begin

        def flight_duration(type):
            def d1():
                return timedelta(minutes=random.randrange(30, 60 * 4))

            def d2():
                return timedelta(minutes=random.randrange(60 * 4, 60 * 8))

            def d3():
                return timedelta(minutes=random.randrange(60 * 8, 60 * 20))

            switcher = {
                1: d1,
                2: d2,
                3: d3,
            }
            func = switcher.get(type)
            duration = func()
            return duration

        crews_ids = []
        for (id,) in Crew.objects.values_list('id'):
            crews_ids.append(id)

        print("Flights:")
        for p in Plane.objects.all():
            flights_count = random.randrange(50, 100)

            dest_time = start_time_min_begin + timedelta(minutes=random.randrange(30,
                                                                                  30 * floor(
                                                                                      begin_duration.total_seconds() / (
                                                                                                  30 * 60)), 30))
            last_date_count = 0
            last_date = dest_time

            start_airport_id = random.randrange(1, airport_count)

            crew_id = random.choice(crews_ids);
            crews_ids.remove(crew_id)
            crew = Crew.objects.get(id=crew_id)

            for i in range(0, flights_count):
                duration = flight_duration(random.choice([1, 1, 1, 1, 1, 2, 2, 3]))
                gaptime = timedelta(minutes=random.randrange(60, 12 * 60))
                start_time = dest_time + gaptime

                if start_time.day == last_date and last_date_count == 4:
                    last_date_count = 0;
                    start_time += timedelta(days=1)

                dest_time = start_time + duration
                if dest_time.day != start_time.day:
                    last_date_count = 0;
                last_date = dest_time.day

                dest_airport_id = random.randrange(1, airport_count - 1)
                if dest_airport_id == start_airport_id:
                    dest_airport_id = airport_count

                f = Flight(plane=p, crew=crew, start_time=timezone.make_aware(start_time, timezone.get_current_timezone()),
                           dest_time=timezone.make_aware(dest_time, timezone.get_current_timezone()),
                           start_airport_id=start_airport_id, dest_airport_id=dest_airport_id)
                print(f.plane.code, f.start_time, f.start_airport_id, f.dest_time, f.dest_airport_id)
                f.save()

                start_airport_id = dest_airport_id
