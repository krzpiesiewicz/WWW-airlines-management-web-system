from datetime import timedelta, datetime

from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models, transaction
from django.db.models import Sum, Q


class Plane(models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    seat_count = models.IntegerField()

class Airport(models.Model):
    name = models.CharField(max_length=100)

class PilotInCommand(models.Model):
    first_names = models.CharField(max_length=50, validators=[MinLengthValidator(1)], null=True)
    last_name = models.CharField(max_length=50, validators=[MinLengthValidator(1)], null=True)

    class Meta:
        unique_together = ('first_names', 'last_name')

    def clean(self):
        if self.first_names == "" or self.last_name == "":
            raise ValidationError("first_names or lastname blank")

class Crew(models.Model):
    pilot_in_command = models.ForeignKey(PilotInCommand, on_delete=models.PROTECT)

class CrewMember(models.Model):
    first_names = models.CharField(max_length=50, validators=[MinLengthValidator(1)], null=True)
    last_name = models.CharField(max_length=50, validators=[MinLengthValidator(1)], null=True)
    crew = models.ForeignKey(Crew, on_delete=models.CASCADE)

    def clean(self):
        if self.first_names == "" or self.last_name == "":
            raise ValidationError("first_names or lastname blank")

class Flight(models.Model):
    start_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='%(class)s_start')
    dest_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='%(class)s_dest')

    start_time = models.DateTimeField()
    dest_time = models.DateTimeField()

    plane = models.ForeignKey(Plane, on_delete=models.CASCADE)

    crew = models.ForeignKey(Crew, on_delete=models.PROTECT, null=True, blank=True, default=None)

    @transaction.atomic
    def free_seats(self):
        booked_seats = Ticket.objects.filter(flight_id=self.id).values('number_of_seats') \
            .aggregate(Sum('number_of_seats'))['number_of_seats__sum']
        if booked_seats == None:
            booked_seats = 0;
        return self.plane.seat_count - booked_seats

    def clean(self):
        if self.start_time + timedelta(minutes=30) > self.dest_time:
            raise ValidationError("start_time should be at least 30 minutes earlier than dest_time")

        flights = Flight.objects.filter(plane=self.plane, start_time__range=[self.start_time, self.dest_time], \
                                        dest_time__range=[self.start_time, self.dest_time]).exclude(id=self.id)
        if flights.count() > 0:
            raise ValidationError("A plane can operate only one flight in a moment")

        almost_one_day = timedelta(hours=23, minutes=59, seconds=59)

        d = datetime.combine(self.start_time.date(), datetime.min.time())

        flights = Flight.objects.filter(plane=self.plane).\
            filter(Q(start_time__range=[d, d + almost_one_day]) | Q(dest_time__range=[d, d + almost_one_day])).\
            exclude(id=self.id)

        if flights.count() >= 4:
            raise ValidationError("A plane has to operate at most 4 times a day")

        if self.start_time.date() != self.dest_time.date():
            d = datetime.combine(self.dest_time.date(), datetime.min.time())
            flights = Flight.objects.filter(plane=self.plane).\
                filter(Q(start_time__range=[d, d + almost_one_day]) | Q(dest_time__range=[d, d + almost_one_day])).\
                exclude(id=self.id)

            if (flights.count() >= 4):
                raise ValidationError("A plane has to operate at most 4 times a day")

        flights = Flight.objects.filter(Q(start_time__lte=self.dest_time) & Q(dest_time__gte=self.start_time)
                                        & Q(crew=self.crew)). \
            exclude(id=self.id)

        if flights.exists():
            raise ValidationError("A crew can be on only one board at the moment")


    def __str__(self):
        return "Flight id %d" % self.id


class Ticket(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    number_of_seats = models.PositiveIntegerField()
    passenger = models.CharField(max_length=70)

    def clean(self):
        if self.number_of_seats > self.flight.plane.seat_count:
            raise ValidationError(
                "A number of seats in ticket has to be equal or less than the number of all seats on board (%d)" \
                % self.flight.plane.seat_count)
        booked_seats_without_these_ones = \
            Ticket.objects.filter(flight=self.flight).exclude(id=self.id).values('number_of_seats') \
                .aggregate(Sum('number_of_seats'))['number_of_seats__sum']
        if booked_seats_without_these_ones == None:
            booked_seats_without_these_ones = 0
        free_seats_without_these_ones = self.flight.plane.seat_count - booked_seats_without_these_ones
        if (self.number_of_seats > free_seats_without_these_ones):
            raise ValidationError(
                "A number of seats in ticket has to be equal or less than the number of all free seats (%d)" \
                % free_seats_without_these_ones)