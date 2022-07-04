import argparse
import datetime
import os
import sys
import random
import time


class User:
    def __init__(self, sui, start_date, records=None):
        if records is None:
            records = []
        self.sui = sui
        self.start_date = start_date
        # trials last 90 days
        self.end_date = self.start_date + (90 * 24 * 60 * 60)
        self.records = records


class Record:
    def __init__(self, sui, timestamp, duration, hr, hrv, qtc, qrs, spo2, dbp, sbp, pwv, sv, co, cardiac_index,
                 sv_index, ptt, pat, seat_weight, r_peak_loc, respiration_rate, ecg_elec_imped, ppg_ir_dc,
                 ppg_ir_pulsatile, ppg_red_dc, ppg_red_pulsatile, bcg_rms, q_amp, q_loc, r_amp, r_loc, s_amp, s_loc,
                 t_peak_amp, t_peak_loc, t_end_amp, t_end_loc, h_amp, h_loc, i_amp, i_loc, j_amp, j_loc, ir_min_tan_amp,
                 ir_min_tan_loc, ir_peak_amp, ir_peak_loc, red_min_tan_amp, red_min_tan_loc, red_peak_amp,
                 red_peak_loc, channel_format):
        self.sui = sui
        self.timestamp = timestamp
        self.duration = duration
        self.hr = hr
        self.hrv = hrv
        self.qtc = qtc
        self.qrs = qrs
        self.spo2 = spo2
        self.dbp = dbp
        self.sbp = sbp
        self.pwv = pwv
        self.sv = sv
        self.co = co
        self.cardiac_index = cardiac_index
        self.sv_index = sv_index
        self.ptt = ptt
        self.pat = pat
        self.seat_weight = seat_weight
        self.r_peak_loc = r_peak_loc
        self.respiration_rate = respiration_rate
        self.ecg_elec_imped = ecg_elec_imped
        self.ppg_ir_dc = ppg_ir_dc
        self.ppg_ir_pulsatile = ppg_ir_pulsatile
        self.ppg_red_dc = ppg_red_dc
        self.ppg_red_pulsatile = ppg_red_pulsatile
        self.bcg_rms = bcg_rms
        self.q_amp = q_amp
        self.q_loc = q_loc
        self.r_amp = r_amp
        self.r_loc = r_loc
        self.s_amp = s_amp
        self.s_loc = s_loc
        self.t_peak_amp = t_peak_amp
        self.t_peak_loc = t_peak_loc
        self.t_end_amp = t_end_amp
        self.t_end_loc = t_end_loc
        self.h_amp = h_amp
        self.h_loc = h_loc
        self.i_amp = i_amp
        self.i_loc = i_loc
        self.j_amp = j_amp
        self.j_loc = j_loc
        self.ir_min_tan_amp = ir_min_tan_amp
        self.ir_min_tan_loc = ir_min_tan_loc
        self.ir_peak_amp = ir_peak_amp
        self.ir_peak_loc = ir_peak_loc
        self.red_min_tan_amp = red_min_tan_amp
        self.red_min_tan_loc = red_min_tan_loc
        self.red_peak_amp = red_peak_amp
        self.red_peak_loc = red_peak_loc
        self.channel_format = channel_format


def query_yes_no(question):
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    prompt = " [y/n] "
    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


def main():
    parser = argparse.ArgumentParser(description='Parses a csv file from the seats experiment.')

    parser.add_argument("output_file", help="The output file to write to.")

    args = parser.parse_args()

    # check if the output file exists and is writable
    if os.path.exists(args.output_file):
        # ask to overwrite if the file exists
        if not query_yes_no("Output file already exists. Overwrite?"):
            exit(1)
    # if not os.access(args.output_file, os.W_OK):
    #     print("Output file is not writable.")
    #     exit(1)

    headers = "clinical.sui	clinical.timestamp	clinical.duration	clinical.hr	clinical.hrv	clinical.qtc	" \
              "clinical.qrs	clinical.spo2	clinical.dbp	clinical.sbp	clinical.pwv	clinical.sv	clinical.co	" \
              "clinical.cardiac_index	clinical.sv_index	clinical.ptt	clinical.pat	clinical.seat_weight	" \
              "clinical.r_peak_loc	clinical.respiration_rate	clinical.ecg_elec_imped	low_level.ppg_ir_dc	" \
              "low_level.ppg_ir_pulsatile	low_level.ppg_red_dc	low_level.ppg_red_pulsatile	low_level.bcg_rms	" \
              "ecg.q_amp	ecg.q_loc	ecg.r_amp	ecg.r_loc	ecg.s_amp	ecg.s_loc	ecg.t_peak_amp	ecg.t_peak_loc	" \
              "ecg.t_end_amp	ecg.t_end_loc	bcg.h_amp	bcg.h_loc	bcg.i_amp	bcg.i_loc	bcg.j_amp	bcg.j_loc	" \
              "ppg.ir_min_tan_amp	ppg.ir_min_tan_loc	ppg.ir_peak_amp	ppg.ir_peak_loc	ppg.red_min_tan_amp	" \
              "ppg.red_min_tan_loc	ppg.red_peak_amp	ppg.red_peak_loc	channel_format".split('\t')

    user_list = []

    # generate a random 4-digit number
    prefix = str(random.randint(1000, 9999)) + "_"

    # generate 10-20 random SUIs by combing the prefix with a random 2-digit number
    # and a random start date as Unix timestamp within the past year
    time_one_year_ago = int(round(time.time())) - 60 * 60 * 24 * 365
    time_now = int(round(time.time()))
    for i in range(random.randint(10, 20)):
        sui = prefix + str(random.randint(0, 99))
        start_date = random.randint(time_one_year_ago, time_now)
        user_list.append(User(sui, start_date))

    # write the output file
    with open(args.output_file, 'w') as f:
        f.write(','.join(headers) + '\n')

        # write 10_000 to 15_000 random records
        for i in range(random.randint(10000, 15000)):
            # pick a random user from the list
            user = random.choice(user_list)
            sui = user.sui

            # generate a random timestamp within the user's start date and end date
            start_date = user.start_date
            end_date = user.start_date + 60 * 60 * 24 * 90
            timestamp = random.randint(start_date, end_date)

            # convert timestamp to readable date
            timestamp = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

            # generate a random duration between 30 and 300 seconds
            duration = random.randint(30, 300)

            # generate a random heart rate between 40 and 130 bpm
            hr = random.randint(40, 130)

            # generate a random heart rate variability between 0 and 100 bpm
            hrv = random.randint(0, 100)

            # generate a random QTc between 0.4 and 0.6, with a 20% chance of being missing
            qtc = random.random() * 0.2 + 0.4 if random.random() > 0.2 else ""

            # generate a random QRS duration between 0.05 and 0.1, with a 20% chance of being missing
            qrs = random.random() * 0.05 + 0.05 if random.random() > 0.2 else ""

            has_spo2 = random.random() > 0.01

            spo2 = ""
            dbp = ""
            sbp = ""
            pwv = ""
            sv = ""
            co = ""

            if has_spo2:
                # generate a random SPO2 between 90 and 100%, with a 99% chance of being missing
                spo2 = random.randint(90, 100)

                # generate a random DBP between 60 and 80 mmHg, with a 99% chance of being missing
                dbp = random.randint(60, 80)

                # generate a random SBP between 120 and 140 mmHg, with a 99% chance of being missing
                sbp = random.randint(120, 140)

                # generate a random PWV between 0 and 0.5, with a 99% chance of being missing
                pwv = random.random() * 0.5

                # generate a random SV between 0 and 0.5, with a 99% chance of being missing
                sv = random.random() * 0.5

                # generate a random CO between 0 and 0.5, with a 99% chance of being missing
                co = random.random() * 0.5

            cardiac_index = ""
            sv_index = ""

            # generate a random PTT between 0 and 0.5, with an 80% chance of being missing
            ptt = random.random() * 0.5 if random.random() > 0.2 else ""

            # generate a random PAT between 0 and 0.5, with an 80% chance of being missing
            pat = random.random() * 0.5 if random.random() > 0.2 else ""

            # generate a random seat weight between 80 and 150 kg
            seat_weight = random.randint(80, 150)

            r_peak_loc = "List (" + str(random.randint(30, 250)) + ")"

            respiration_rate = ""
            ecg_elec_imped = ""

            has_low_level = random.random() < 0.10

            low_level_ppg_ir_dc = ""
            low_level_ppg_ir_pulsatile = ""
            low_level_ppg_red_dc = ""
            low_level_ppg_red_pulsatile = ""
            low_level_bcg_rms = ""

            if has_low_level:
                low_level_ppg_ir_dc = random.randint(400, 600)
                low_level_ppg_ir_pulsatile = random.random() * 1 + 0.4
                low_level_ppg_red_dc = random.randint(50, 600)
                low_level_ppg_red_pulsatile = random.random() * 0.3
                low_level_bcg_rms = random.random() + 0.5

            has_ecg = random.random() > 0.02

            ecg_q_amp = ""
            ecg_q_loc = ""
            ecg_r_amp = ""
            ecg_r_loc = ""
            ecg_s_amp = ""
            ecg_s_loc = ""
            ecg_t_peak_amp = ""
            ecg_t_peak_loc = ""
            ecg_t_end_amp = ""
            ecg_t_end_loc = ""

            if has_ecg:
                ecg_q_amp = random.randint(-5, 15)
                ecg_q_loc = random.randint(-45, -25)
                ecg_r_amp = random.randint(70, 150)
                ecg_r_loc = 0
                ecg_s_amp = random.randint(-50, -10)
                ecg_s_loc = random.randint(40, 70)
                ecg_t_peak_amp = random.randint(-20, -10)
                ecg_t_peak_loc = random.randint(80, 250)
                ecg_t_end_amp = random.randint(-10, 10)
                ecg_t_end_loc = random.randint(300, 600)

            has_bcg = random.random() > 0.5

            bcg_h_amp = ""
            bcg_h_loc = ""
            bcg_i_amp = ""
            bcg_i_loc = ""
            bcg_j_amp = ""
            bcg_j_loc = ""

            if has_bcg:
                bcg_h_amp = random.random()
                bcg_h_loc = random.randint(70, 150)
                bcg_i_amp = random.random() * -1
                bcg_i_loc = random.randint(100, 150)
                bcg_j_amp = random.random()
                bcg_j_loc = random.randint(150, 300)

            has_ppg = random.random() > 0.6

            ppg_ir_min_amp = ""
            ppg_ir_min_loc = ""
            ppg_ir_peak_amp = ""
            ppg_ir_peak_loc = ""
            ppg_ir_red_min_amp = ""
            ppg_ir_red_min_loc = ""
            ppg_ir_red_peak_amp = ""
            ppg_ir_red_peak_loc = ""

            if has_ppg:
                ppg_ir_min_amp = random.random()
                ppg_ir_min_loc = random.randint(100, 300)
                ppg_ir_peak_amp = random.random()
                ppg_ir_peak_loc = random.randint(100, 300)
                ppg_ir_red_min_amp = random.random()
                ppg_ir_red_min_loc = random.randint(100, 300)
                ppg_ir_red_peak_amp = random.random()
                ppg_ir_red_peak_loc = random.randint(100, 300)

            channel_format = "<" + str(random.randint(10, 30)) + "000f"

            # create a new row in the CSV file
            f.write(sui + "," + str(timestamp) + "," + str(duration) + "," + str(hr) + "," + str(hrv) + "," +
                    str(qtc) + "," + str(qrs) + "," + str(spo2) + "," + str(dbp) + "," + str(sbp) + "," + str(pwv) +
                    "," + str(sv) + "," + str(co) + "," + str(cardiac_index) + "," + str(sv_index) + "," + str(ptt) +
                    "," + str(pat) + "," + str(seat_weight) + "," + r_peak_loc + "," + str(respiration_rate) + "," +
                    str(ecg_elec_imped) + "," + str(low_level_ppg_ir_dc) + "," + str(low_level_ppg_ir_pulsatile) + "," +
                    str(low_level_ppg_red_dc) + "," + str(low_level_ppg_red_pulsatile) + "," + str(low_level_bcg_rms) +
                    "," + str(ecg_q_amp) + "," + str(ecg_q_loc) + "," + str(ecg_r_amp) + "," + str(ecg_r_loc) + "," +
                    str(ecg_s_amp) + "," + str(ecg_s_loc) + "," + str(ecg_t_peak_amp) + "," + str(ecg_t_peak_loc) + "," +
                    str(ecg_t_end_amp) + "," + str(ecg_t_end_loc) + "," + str(bcg_h_amp) + "," + str(bcg_h_loc) + "," +
                    str(bcg_i_amp) + "," + str(bcg_i_loc) + "," + str(bcg_j_amp) + "," + str(bcg_j_loc) + "," +
                    str(ppg_ir_min_amp) + "," + str(ppg_ir_min_loc) + "," + str(ppg_ir_peak_amp) + "," +
                    str(ppg_ir_peak_loc) + "," + str(ppg_ir_red_min_amp) + "," + str(ppg_ir_red_min_loc) + "," +
                    str(ppg_ir_red_peak_amp) + "," + str(ppg_ir_red_peak_loc) + "," + str(channel_format) + "\n")


if __name__ == '__main__':
    main()
