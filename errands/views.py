from __future__ import print_function
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from errands.models import Errand, Piece, Std
from datetime import datetime as dt, timedelta as td
from django.urls import reverse
from django.http import HttpResponsePermanentRedirect as httpRPR, HttpResponse as httpR
from home.views import in_session
import json
import math


def all_errands(request):
    errands = Errand.objects.all()
    return render(request, 'errands/all.html', {'errands': errands})


def touch(request, pk):
    # User Session Check
    if not in_session(request):
        return render(request, 'home/login.html', {'Client_Site': str(request.get_raw_uri())})

    # pk >= 0 from regex
    int__pk = int(pk)

    if request.method == 'GET':
        # New errand
        if int__pk == 0:
            errand = None
            old_pieces = []

            return render(request, 'errands/touch.html', {'errand': errand,
                                                          'old_pieces': old_pieces,
                                                          })
        # Old errand
        else:
            errand = get_object_or_404(Errand, pk=pk)
            old_pieces = []
            for piece in errand.piece_set.all():
                piece.epoch_date = piece.epoch_date.strftime(Std.output_d_format)
                piece.epoch_time = piece.epoch_time.strftime(Std.output_t_format)
                if piece.end_date is not None:
                    piece.end_date = piece.end_date.strftime(Std.output_d_format)
                else:
                    piece.end_date = ''

                if piece.end_time is not None:
                    piece.end_time = piece.end_time.strftime(Std.output_t_format)
                else:
                    piece.end_time = ''

                old_pieces.append(piece)

            return render(request, 'errands/touch.html', {'errand': errand,
                                                          'old_pieces': old_pieces,
                                                          })
    else:
        return render(request, 'home/invalid_access.html')


# TODO: validate the inputs for more security
def process_touch(request):
    # User Session Check
    if not in_session(request):
        return render(request, 'home/login.html', {'Client_Site': str(request.get_raw_uri())})

    # pk >= 0 from regex
    if request.method == 'POST':

        int__flag = int(request.POST['Flag'])
        input_errand = json.loads(request.POST['Errand'])
        input_old_pieces = json.loads(request.POST['Old_Pieces'])
        input_new_pieces = json.loads(request.POST['New_Pieces'])

        # New Errand
        if input_errand[Std.Keys.pk] == 0:
            # new errand
            errand = Errand()
            errand.set(tag=input_errand[Std.Keys.tag],
                       comment=input_errand[Std.Keys.comment],
                       misc={})
            errand.save()

            for input_new_piece in input_new_pieces:
                new_piece = Piece()
                new_piece.set(tag=input_new_piece[Std.Keys.tag],
                              comment=input_new_piece[Std.Keys.comment],
                              misc={},
                              epoch_date=dt.strptime(input_new_piece[Std.Keys.epoch_date], Std.input_d_format).date(),
                              epoch_time=dt.strptime(input_new_piece[Std.Keys.epoch_time], Std.input_t_format).time(),
                              time_period=td(days=int(input_new_piece[Std.Keys.time_period][Std.Keys.days]),
                                             seconds=int(input_new_piece[Std.Keys.time_period][Std.Keys.seconds])
                                             ),
                              duration=td(days=int(input_new_piece[Std.Keys.duration][Std.Keys.days]),
                                          seconds=int(input_new_piece[Std.Keys.duration][Std.Keys.seconds])
                                          ),
                              end_date=input_new_piece[Std.Keys.end_date],
                              end_time=input_new_piece[Std.Keys.end_time],
                              )
                new_piece.save()
                errand.piece_set.add(new_piece)
        # Old Errand
        else:
            # (possible) old errand
            errand = get_object_or_404(Errand, pk=input_errand[Std.Keys.pk])
            errand.set(tag=input_errand[Std.Keys.tag],
                       comment=input_errand[Std.Keys.comment],
                       misc={})
            errand.save()

            old_pieces = errand.piece_set.all()
            updated_pks = []

            # Update Old Pieces
            for input_old_piece in input_old_pieces:
                # take a look on updated pieces
                updated_pks.append(int(input_old_piece[Std.Keys.pk]))
                # updating old pieces
                old_piece = Piece.objects.get(pk=input_old_piece[Std.Keys.pk])
                old_piece.set(tag=input_old_piece[Std.Keys.tag],
                              comment=input_old_piece[Std.Keys.comment],
                              misc={},
                              epoch_date=dt.strptime(input_old_piece[Std.Keys.epoch_date], Std.input_d_format).date(),
                              epoch_time=dt.strptime(input_old_piece[Std.Keys.epoch_time], Std.input_t_format).time(),
                              time_period=td(days=int(input_old_piece[Std.Keys.time_period][Std.Keys.days]),
                                             seconds=int(input_old_piece[Std.Keys.time_period][Std.Keys.seconds])
                                             ),
                              duration=td(days=int(input_old_piece[Std.Keys.duration][Std.Keys.days]),
                                          seconds=int(input_old_piece[Std.Keys.duration][Std.Keys.seconds])
                                          ),
                              end_date=input_old_piece[Std.Keys.end_date],
                              end_time=input_old_piece[Std.Keys.end_time],
                              )
                old_piece.save()

            # Delete Old Pieces
            for old_piece in old_pieces:
                # Check whether it is updated or not
                delete_this = True
                for updated_pk in updated_pks:
                    if updated_pk == old_piece.pk:
                        delete_this = False
                        break
                # Not updated then delete
                if delete_this:
                    old_piece.delete()

            # Create New Pieces
            for input_new_piece in input_new_pieces:
                new_piece = Piece()
                new_piece.set(tag=input_new_piece[Std.Keys.tag],
                              comment=input_new_piece[Std.Keys.comment],
                              misc={},
                              epoch_date=dt.strptime(input_new_piece[Std.Keys.epoch_date], Std.input_d_format).date(),
                              epoch_time=dt.strptime(input_new_piece[Std.Keys.epoch_time], Std.input_t_format).time(),
                              time_period=td(days=int(input_new_piece[Std.Keys.time_period][Std.Keys.days]),
                                             seconds=int(input_new_piece[Std.Keys.time_period][Std.Keys.seconds])
                                             ),
                              duration=td(days=int(input_new_piece[Std.Keys.duration][Std.Keys.days]),
                                          seconds=int(input_new_piece[Std.Keys.duration][Std.Keys.seconds])
                                          ),
                              end_date=input_new_piece[Std.Keys.end_date],
                              end_time=input_new_piece[Std.Keys.end_time],
                              )
                new_piece.save()
                errand.piece_set.add(new_piece)

        if int__flag == 0:
            return httpRPR(reverse('errands:touch_errand', kwargs={'pk': errand.pk}))
        elif int__flag == 1:
            return httpRPR(reverse('errands:all_errands'))
        elif int__flag == 2:
            return httpRPR(reverse('time_table:scrolling_stubs'))

    else:
        return render(request, 'home/invalid_access.html')


def delete_errand(request):
    # User Session Check
    if not in_session(request):
        return render(request, 'home/login.html')

    if request.method == 'POST':
        if 'pk' in request.POST:
            try:
                del_errand = Errand.objects.get(pk=request.POST['pk'])
                del_errand.delete()
                return httpRPR(reverse('errands:all_errands'))
            except ObjectDoesNotExist:
                return render(request, 'home/invalid_access.html')
    else:
        return render(request, 'home/invalid_access.html')


def read_errand(request, pk):
    json_dict = {}

    try:
        errand = Errand.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return httpR(-1)

    json_dict['pk'] = errand.pk
    json_dict['errand'] = errand.description

    if 'pieces_also' in request.GET:
        if request.GET['pieces_also'] == '1':
            pieces_also = 1
        else:
            pieces_also = 0
    else:
        pieces_also = 0

    if pieces_also == 1:
        piece_descriptions = []
        pieces = errand.piece_set.all()
        for piece in pieces:
            piece_description = json.loads(piece.description)
            piece_description['pk'] = piece.pk
            piece_descriptions.append(piece_description)

        json_dict['pieces'] = piece_descriptions

    json_string = json.dumps(json_dict)
    return httpR(json_string)


def read_piece(request, pk):
    try:
        piece = Piece.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return httpR(-1)

    desc = json.loads(piece.description)
    desc['pk'] = piece.pk
    desc['errand_pk'] = piece.errand_id
    desc['errand_tag'] = piece.errand.tag
    desc['errand_comment'] = piece.errand.comment
    json_string = json.dumps(desc)
    return httpR(json_string)


def do_stubs_intersect(e1, e2):
    e1_epoch = e1['epoch']
    e2_epoch = e2['epoch']
    e1_end = e1['end']
    e2_end = e2['end']
    return e1_epoch <= e2_epoch <= e1_end \
           or e1_epoch <= e2_end <= e1_end \
           or e2_epoch <= e1_epoch <= e2_end \
           or e2_epoch <= e1_end <= e2_end


def td_in_microsecond(timedelta):
    return timedelta.days * 86400000000 + timedelta.seconds * 1000000 + timedelta.microseconds


def get_stubs_in_range(lb, ub):
    event_stubs = []
    lanes = []
    task_stubs = []

    all_pieces = Piece.objects.all()

    # Creating Stubs within the given Time Range
    for piece in all_pieces:
        # Non Repeating
        if piece.is_non_repeating():
            epoch = dt.combine(piece.epoch_date, piece.epoch_time)
            stub = piece.get_stub_which_intersects(epoch, lb, ub)
            if stub is not None:
                # Task Stub
                if piece.is_task():
                    task_stubs.append(stub)
                # Event Stub
                else:
                    event_stubs.append(stub)
        # Repeating
        else:
            init_epoch = dt.combine(piece.epoch_date, piece.epoch_time)
            duration = piece.duration
            # Non - Zero Time Period
            time_period = piece.time_period
            # Starting from init_epoch
            if init_epoch < lb:
                no_of_time_periods = int(math.ceil(float(td_in_microsecond(lb - init_epoch)) / float(
                    td_in_microsecond(time_period))))
                i_epoch = init_epoch + time_period * no_of_time_periods
            elif lb <= init_epoch <= ub:
                i_epoch = init_epoch
            else:
                continue

            # Adding Stubs
            # Task Stubs (Once a task piece always a task piece)
            if piece.is_task():

                # End not Specified
                if piece.get_end_datetime() is None:
                    # Until epoch is equal to or below the upper bound
                    while i_epoch <= ub:
                        # Adding Stubs one by one
                        stub = piece.get_stub_which_intersects(i_epoch, lb, ub)
                        if stub is not None:
                            task_stubs.append(stub)
                        i_epoch += time_period

                # End Specified
                else:
                    end = dt.combine(piece.end_date, piece.end_time)
                    # Until epoch is equal to or below the upper bound and end
                    while i_epoch <= ub and i_epoch <= end:
                        # Adding Stubs one by one
                        stub = piece.get_stub_which_intersects(i_epoch, lb, ub)
                        if stub is not None:
                            task_stubs.append(stub)
                        i_epoch += time_period

            # Event Stubs (Once a event piece always a event piece)
            else:

                # End not Specified
                if piece.get_end_datetime() is None:
                    # Until epoch is equal to or below the upper bound
                    while i_epoch <= ub:
                        # Non Repeating
                        stub = piece.get_stub_which_intersects(i_epoch, lb, ub)
                        if stub is not None:
                            event_stubs.append(stub)
                        i_epoch += time_period
                #
                # End Specified
                else:
                    end = dt.combine(piece.end_date, piece.end_time)
                    # Until epoch is equal to or below the upper bound and end
                    while i_epoch <= ub and i_epoch <= end:
                        # Non Repeating
                        stub = piece.get_stub_which_intersects(i_epoch, lb, ub)
                        if stub is not None:
                            event_stubs.append(stub)
                        i_epoch += time_period

    # Ordering stubs , Creating lanes
    for stub in event_stubs:

        in_some_lane = False
        for lane in lanes:
            in_this_lane = True
            for car in lane:
                if do_stubs_intersect(stub, car):
                    in_this_lane = False
                    break
            # If intersect with no car in this lane
            # Then add the stub in this lane
            if in_this_lane:
                lane.append(stub)
                in_some_lane = True
                break

        # If not in some lane
        # Add a lane
        # Add this stub in that lane
        if not in_some_lane:
            lanes.append([stub])

    # Serializing datetime to json format
    for lane in lanes:
        for stub in lane:
            stub['epoch'] = stub['epoch'].strftime(Std.output_dt_format),
            stub['end'] = stub['end'].strftime(Std.output_dt_format),

    for task_stub in task_stubs:
        task_stub['epoch'] = task_stub['epoch'].strftime(Std.output_dt_format),
        task_stub['end'] = task_stub['end'].strftime(Std.output_dt_format),

    return {'Events': lanes, 'Tasks': task_stubs}


def read_stubs(request):
    """
    :param request:
    :return:
        stubs belonging to the "POSTed ranges"
        in json format
        event-stubs lane wise sorted
        task-stubs separate from event stubs
    """
    try:
        ranges = json.loads(request.GET['ranges'])
        try:
            for range_i in ranges:
                lb = dt.strptime(range_i['LB'], Std.input_dt_format)
                ub = dt.strptime(range_i['UB'], Std.input_dt_format)
                range_i['Stubs'] = get_stubs_in_range(lb, ub)

            return httpR(json.dumps(ranges))

        except ValueError or TypeError:
            return httpR(-1)

    except ValueError or TypeError:
        return httpR(-1)
