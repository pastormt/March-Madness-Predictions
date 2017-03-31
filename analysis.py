import csv
import copy
import matplotlib.pyplot as plt

# create hash table
# expects csv file with ID in column 1, and Value in column 2, with new lines per each ID & Value
# (these are exported as CSVs from the Google Spreadsheets and put in the same directory as this file, analysis.py)
def create_id_score_dict(file_name):
    vals = {}
    with open(file_name, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] != '#N/A':
                teamID = int(row[0])
                val = float(row[1])
                vals[teamID] = val
    return vals

# get tourney seeds
# (basically same fcn as above)
def get_seeds(file_name, tourney_year):
    seeds = {}
    with open(file_name, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            year = int(row[0])
            if year == tourney_year:
                seed = row[1].strip()
                teamID = int(row[2])
                seeds[teamID] = seed
    return seeds

def play_first_four(seeds, vals):
    first_four_winners_and_losers = set()
    winning_teams_seeds = {}
    prev_teamID = None
    prev_seed = None
    prev_length = None
    for teamID, seed in sorted(seeds.items(), key = lambda kv : kv[1]):
        length = len(seed)
        if (length == 4 and prev_length == 4) and (prev_seed[:-1] == seed[:-1]):
            first_four_winners_and_losers.add(teamID)
            first_four_winners_and_losers.add(prev_teamID)
            # take the team that would have won based on the current evaluator
            #print(teamID, seed, vals[teamID])
            #print(prev_teamID, prev_seed, vals[prev_teamID])
            if vals[teamID] >= vals[prev_teamID]:
                winner = teamID
            else:
                winner = prev_teamID
            winning_teams_seeds[winner] = seed[:-1]

        prev_teamID = teamID
        prev_seed = seed
        prev_length = length
    #print(winning_teams_seeds)
    return winning_teams_seeds, first_four_winners_and_losers


def seeds_after_first_four(seeds, winning_first_four):
    adjusted_seeds = copy.deepcopy(seeds)
    for winning_teamID, trimmed_seed in winning_first_four.items():
        for teamID, seed in seeds.items(): #original seeds
            if seed[:-1] == trimmed_seed:
                if teamID != winning_teamID:
                    # this is the losing team... remove it
                    del adjusted_seeds[teamID]
                else:
                    adjusted_seeds[teamID] = trimmed_seed # remove the 'a' or 'b' from the end of the seed

    return adjusted_seeds

# split 64 seeds dictionary into 4 lists (ordered by seed, ascending) of seeds
def split_seeds(seeds):
    four_lists = []

    for teamID, seed in sorted(seeds.items(), key = lambda kv : kv[1]):
        seed_num = seed[1:]
        if seed_num == '01':
            cur_list = []
        cur_list.append(teamID)
        if seed_num == '16':
            four_lists.append(cur_list)

    return four_lists

# note according to TourneySlots.csv file, in final four, W plays X and Y plays Z
def play_sixty_four(lists, vals, seeds):
    team_ranks = {}

    def eliminate_half(four_lists, ranks):
        new_four = []
        for region in four_lists:
            cur_list = []
            length = len(region)
            #print(region)
            for i in range(int(length / 2)):
                #print(region[i], vals[region[i]], region[length - 1 - i], vals[region[length - 1 - i]])
                if vals[region[i]] >= vals[region[length - 1 - i]]:
                    winner = region[i]
                    loser = region[length - 1 - i]
                else:
                    winner = region[length - 1 - i]
                    loser = region[i]

                cur_list.append(winner)
                ranks[loser] = length * 4
            #print(cur_list)
            new_four.append(cur_list)

        return new_four
    # end eliminate_half

    cur_list_length = 16
    while cur_list_length > 1:
        lists = eliminate_half(lists, team_ranks)
        cur_list_length /= 2

    # now each list within lists should have 1 item
    # these are the final four teams
    # and team_ranks is the rank each team achieved... (without the losing members of the final four added yet...)

    # lookup the original seed value of each team in lists, and get the first letter
    # play the one with first letter W play X, Y play Z

    final_four_dict = {}
    for final_four_team in lists:
        # final four team is a list of 1 team (each)
        teamID = final_four_team[0]
        seed_first_letter = seeds[teamID][:1]
        final_four_dict[seed_first_letter] = teamID

    def play_final_four_game(letterA, letterB, final_four_dict, vals, ranks):
        #print(final_four_dict)
        if vals[final_four_dict[letterA]] >= vals[final_four_dict[letterB]]:
            winner = final_four_dict[letterA]
            loser = final_four_dict[letterB]
        else:
            winner = final_four_dict[letterB]
            loser = final_four_dict[letterA]

        ranks[loser] = 4
        return winner

    # final TWO
    teamA = play_final_four_game('W', 'X', final_four_dict, vals, team_ranks)
    teamB = play_final_four_game('Y', 'Z', final_four_dict, vals, team_ranks)

    if vals[teamA] >= vals[teamB]:
        winner = teamA
        loser = teamB
    else:
        winner = teamB
        loser = teamA

    team_ranks[loser] = 2
    team_ranks[winner] = 1

    #print(sorted(team_ranks.items(), key = lambda kv : kv[1]))
    return team_ranks

def get_actual_results(file_name, tourney_year, first_four_winners_and_losers):
    def incr_count(teamID, teams):
        if teamID in teams:
            teams[teamID] += 1
        else:
            if teamID not in first_four_winners_and_losers:
                teams[teamID] = 1
            else:
                teams[teamID] = 0 # dont count the first four game

    teams = {}
    with open(file_name, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            year = int(row[1])
            if year == tourney_year:
                team1 = int(row[2])
                team2 = int(row[4])

                incr_count(team1, teams)
                incr_count(team2, teams)

    '''# testing
    print(sorted(teams.items(), key = lambda kv : kv[1]))
    teams_per_games_count = {}
    for team, games in teams.items():
        if games not in teams_per_games_count:
            teams_per_games_count[games] = 1
        else:
            teams_per_games_count[games] += 1
    print(teams_per_games_count)
    '''# end testing

    # now find first place team
    contenders = set()
    for teamID, games in teams.items():
        if games == 6:
            contenders.add(teamID)

    # now find the game where the contenders play (the championship game) and see who won
    with open(file_name, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            year = int(row[1])
            if year == tourney_year:
                team1 = int(row[2])
                team2 = int(row[4])
                final_teams = set()
                final_teams.add(team1)
                final_teams.add(team2)

                if final_teams == contenders:
                    # then this is the championship game... see who won
                    if int(row[3]) >= int(row[5]):
                        #team 1 won
                        teams[team1] += 1
                    else:
                        teams[team2] += 1

    # now adjust count of games played to a number from 1 - 64 indicating place the team finished
    for teamID, games in teams.items():
        if games == 0:
            teams[teamID] = 68
        else:
            teams[teamID] = int(64 / 2**(games - 1))

    #print(sorted(teams.items(), key = lambda kv : kv[1]))
    return teams

def calculate_precisions(guesses, results):
    def init_formatted(dict):
        new_dict = {}
        n = 64
        while n >= 1:
            new_dict[n] = set()
            n /= 2

        return new_dict

    guesses_formatted = init_formatted(guesses)
    results_formatted = init_formatted(results)

    def fill_formatted(orig_dict, new_dict):
        for teamID, val in orig_dict.items():
            for team_rank, teams_set in new_dict.items():
                if val <= team_rank:
                    new_dict[team_rank].add(teamID)

    fill_formatted(guesses, guesses_formatted)
    fill_formatted(results, results_formatted)

    precisions = {}
    for team_rank, teams_set in guesses_formatted.items():
        #print(team_rank)
        #print(teams_set)
        #print(results_formatted[team_rank])

        in_common = teams_set.intersection(results_formatted[team_rank])
        precisions[team_rank] = len(in_common) / len(teams_set)

    #print(sorted(precisions.items()))
    return precisions

# for combining scores, normalize them first
def normalize(orig_dict):
    normalized = {}

    min_val = min(orig_dict.values())
    max_val = max(orig_dict.values())
    max_minus_min = max_val - min_val

    for key, val in orig_dict.items():
        normalized[key] = (val - min_val) / max_minus_min

    #print(sorted(normalized.items(), key = lambda kv : kv[1], reverse=True))
    return normalized

def normalize_list(orig_list):
    normalized = []

    min_val = min(orig_list)
    max_val = max(orig_list)
    max_minus_min = max_val - min_val

    for val in orig_list:
        normalized.append((val - min_val) / max_minus_min)

    #print(sorted(normalized.items(), key = lambda kv : kv[1], reverse=True))
    return normalized



# getting point differentials...
def get_avg_pt_diffs(file_name, year):

    def add_game(teamID, scored, allowed, pts_scored, pts_allowed, num_games):
        if teamID in pts_scored:
            # than in all 3, so could have tested any of the dicts
            pts_scored[teamID] += scored
            pts_allowed[teamID] += allowed
            num_games[teamID] += 1
        else:
            pts_scored[teamID] = scored
            pts_allowed[teamID] = allowed
            num_games[teamID] = 1


    pts_scored = {}
    pts_allowed = {}
    num_games = {}

    with open(file_name, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            if int(row[0]) == year:
                team1 = int(row[2])
                team1_scored = int(row[3])
                team1_allowed = int(row[5])

                team2 = int(row[4])
                team2_scored = int(row[5])
                team2_allowed = int(row[3])

                add_game(team1, team1_scored, team1_allowed, pts_scored, pts_allowed, num_games)
                add_game(team2, team2_scored, team2_allowed, pts_scored, pts_allowed, num_games)

    teams_pt_diffs = {}

    for teamID, games in num_games.items():
        teams_pt_diffs[teamID] = (pts_scored[teamID] - pts_allowed[teamID]) / games

    #print(sorted(teams_pt_diffs.items(), key = lambda kv : kv[1], reverse=True))
    return teams_pt_diffs

# if a teamID does not exist in ALL rating systems passed to combine, it should not be included in the returned dictionary
# which will cause an error later if the team turns out to be in the tournament...
# rather than not knowing that the team was missing from one or more of the scoring systems
def combine(*args):
    combined = {}

    ids = set()
    # get keys in any of *args
    for arg in args:
        for key in arg:
            ids.add(key)

    for key in ids:
        val = 0
        for arg in args:
            try:
                val += arg[key]
            except KeyError:
                val = None # if key is not in each scoring system (arg), then combined val should not exist
                break

        if val != None:
            combined[key] = val

    return combined

# since lower ranks are better, but higher scores are better -- this fcn makes it so that higher ranks are better
# ie if ranks are out of 68, makes a rank of 1 into a rank of 68, and so on
def adjust_ranks(orig_dict):
    new_dict = {}

    min_val = min(orig_dict.values())
    max_val = max(orig_dict.values())

    for teamID, rank in orig_dict.items():
        new_dict[teamID] = max_val - (rank - min_val)

    return new_dict

def scores_to_adj_ranks(orig_dict):
    adj_ranks = {}

    rank = 1 # since this is adj ranks, 1 is the WORST rank -- like adjust_ranks fcn above
    # to align with scores, where greater is better
    for teamID, score in sorted(orig_dict.items(), key = lambda kv : kv[1]):
        # reverse = False so that the team with the lowest score has a rank of 1
        # since, again, these are adjusted ranks... and higher ranks here are better
        adj_ranks[teamID] = rank
        rank += 1

    return adj_ranks

def run_simulation(prediction_data, year):
    seeds = get_seeds('./data/Seeds.csv',year)
    winning_first_four, first_four_winners_and_losers = play_first_four(seeds, prediction_data)
    adjusted_seeds = seeds_after_first_four(seeds, winning_first_four)
    four_lists = split_seeds(adjusted_seeds)
    #print(sorted(adjusted_seeds.items(), key = lambda kv : kv[1]))
    #print(four_lists)
    guesses = play_sixty_four(four_lists, prediction_data, seeds)
    results = get_actual_results('./data/March_Madness_data.csv',year, first_four_winners_and_losers)
    precisions = calculate_precisions(guesses, results)
    print(sorted(precisions.items()))
    return precisions


def run_all():
    systems = { 'ESPN' : [], 'Seeding' : [], 'SOS' : [], 'PtDiff' : [], 'SC_1' : [], 'RC_1' : [], 'SC_2' : [], 'RC_2' : [] }

    pt_diffs_list = [0 for i in range(0, 68)]
    sos_list = [0 for i in range(0, 68)]
    bpis_list = [0 for i in range(0, 68)]
    seeding_list = [0 for i in range(0, 68)]

    def update_system_scoring_list(holder_list, current_list, seeding):
        i = 0
        for teamID, val in sorted(current_list.items(), key = lambda kv : kv[1], reverse=True):
            if teamID in seeding: # than they are one of the 68
                holder_list[i] += val

                i += 1

    year = 2012
    start_year = year

    while year <= 2015:
        print(year)
        str_year = str(year)
        # bpi predicting alone
        bpis = create_id_score_dict('./data/' + str_year + '_bpi.csv')
        print("ESPN BPI")
        systems['ESPN'].append(run_simulation(bpis, year))

        # seeding predicting alone
        seeding = create_id_score_dict('./data/' + str_year + '_seeding.csv')
        seeding = adjust_ranks(seeding) # to reverse seeds, making higher seeds better, to work with simulation functions
        print("Seeding")
        systems['Seeding'].append(run_simulation(seeding, year))

        # avg point differentials per team in the regular season
        pt_diffs = get_avg_pt_diffs('./data/RegularSeasonCompactResults.csv',year)
        pt_diffs_norm = normalize(pt_diffs)
        sos = create_id_score_dict('./data/' + str_year + '_sos.csv')
        sos_norm = normalize(sos)

        # for Rank-Score functions
        update_system_scoring_list(bpis_list, bpis, seeding)
        update_system_scoring_list(seeding_list, seeding, seeding)
        update_system_scoring_list(pt_diffs_list, pt_diffs, seeding)
        update_system_scoring_list(sos_list, sos, seeding)

        # sos
        print("Strength of Schedule")
        systems['SOS'].append(run_simulation(sos_norm, year))

        # avg. reg season pt diff.
        print("Point differential")
        systems['PtDiff'].append(run_simulation(pt_diffs_norm, year))

        # score combination of regualr season point differential, regular season strength of schedule
        combined = combine(sos_norm, pt_diffs_norm)
        print("Score combination of SOS and Point differential")
        systems['SC_1'].append(run_simulation(combined, year))

        # score combination of reg season pt diff, sos, AND SEEDING
        seeding = normalize(seeding) # ranks have already been adjusted so that higher ranks are better
        combined = combine(sos_norm, pt_diffs_norm, seeding)
        print("Score combination of SOS, Point differential, and Seeding")
        systems['SC_2'].append(run_simulation(combined, year))

        # rank combination of pt diff and sos
        pt_diffs_norm = scores_to_adj_ranks(pt_diffs)
        pt_diffs_norm = normalize(pt_diffs_norm)
        sos_norm = scores_to_adj_ranks(sos)
        sos_norm = normalize(sos_norm)
        combined = combine(sos_norm, pt_diffs_norm)
        print("Rank combination of SOS and Point Differential")
        systems['RC_1'].append(run_simulation(combined, year))

        # rank combination of reg season pt diff, sos, AND SEEDING
        combined = combine(sos_norm, pt_diffs_norm, seeding)
        print("Rank combination of SOS, Point differential, and Seeding")
        systems['RC_2'].append(run_simulation(combined, year))

        year += 1

    ### averaging precisions at each k for each system
    print("System averages...")
    for system, precisions_set in sorted(systems.items(), key = lambda kv : kv[0]):
        print(system)

        new_dict = {} # to hold averages

        n = 64
        while n >= 1:
            new_dict[n] = 0
            n /= 2

        for single_precisions_set in precisions_set:
            for k, precision_calc in single_precisions_set.items():
                new_dict[k] += precision_calc

        for k, precision_calc in new_dict.items():
            new_dict[k] /= (year - start_year)

        print(sorted(new_dict.items(), key = lambda kv : kv[0]))

    # now normalize the scores of each list of runs of each scoring system (for the rank-score functions)
    # then plot then and calculate cognitive diversity
    pt_diffs_list = normalize_list(pt_diffs_list)
    sos_list = normalize_list(sos_list)
    seeding_list = normalize_list(seeding_list)
    bpis_list = normalize_list(bpis_list)

    # calculate cog diversity between sos and avg pt differentials
    cog_div = 0
    for i in range(0, len(sos_list)):
        cog_div += (sos_list[i] - pt_diffs_list[i])**2

    cog_div = cog_div**(1/2)
    print("Cognitive Diversity of SOS and Avg. Pt. Differential =", cog_div)

    cog_div = 0
    for i in range(0, len(sos_list)):
        cog_div += (sos_list[i] - seeding_list[i])**2

    cog_div = cog_div**(1/2)
    print("Cognitive Diversity of SOS and Seeding =", cog_div)

    cog_div = 0
    for i in range(0, len(sos_list)):
        cog_div += (pt_diffs_list[i] - seeding_list[i])**2

    cog_div = cog_div**(1/2)
    print("Cognitive Diversity of Avg. Pt Differential and Seeding =", cog_div)

    #plot rank-score functions
    plt.plot([i for i in range(0, len(pt_diffs_list))], pt_diffs_list, label='Avg. Pt. Differential')
    plt.plot([i for i in range(0, len(sos_list))], sos_list, label='Strength of Schedule')
    plt.plot([i for i in range(0, len(seeding_list))], seeding_list, label='Seeding')
    plt.plot([i for i in range(0, len(bpis_list))], bpis_list, label='ESPN Basketball Power Index')
    plt.title('Rank-score functions')
    plt.xlabel('rank')
    plt.ylabel('normalized score')
    plt.legend()
    plt.show()

run_all()

####
# watch out for any seeded teams that still have #N/As in whichever data (CSV) you're using...
# would have to go back and make sure they have a match to a kaggle ID... only a few that don't
