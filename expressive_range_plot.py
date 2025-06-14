from pcgrl import Game
from pcgrl.Utils import *
from pcgrl.BasePCGRLEnv import Experiment
from pcgrl.envs.zelda import ZeldaLevelObjects as zelda
from pcgrl.envs.mazecoin import MazeCoinLevelObjects as mazecoin
from pcgrl import *
from pcgrl.BasePCGRLEnv import *
from pcgrl.Utils import cum_mean
import pandas as pd
from pcgrl.log import ResultsWriter
from pcgrl.wrappers import WrappersType
from utils import * 


import matplotlib.pyplot as plt
import matplotlib.tri as tri
import csv

class ExpressiveRangePlot:
    
    def __init__(self, 
                results_dir = "./results/",
                total_timesteps = 50000,              
                learning_rate: float = 2.5e-4, 
                n_steps:int   = 128,                                                        
                batch_size:int = 64,
                n_epochs:int = 10,                                          
                act_func = ActivationFunc.SIGMOID.value,
                entropy_min:int = 1.80,
                envs = [Game.ZELDA.value, Game.MINIMAP.value, Game.MAZECOIN.value, Game.MAZE.value, Game.DUNGEON.value],
                representations = [Behaviors.NARROW_PUZZLE.value, Behaviors.WIDE_PUZZLE.value],
                observations = [WrappersType.MAP.value],              
                agents   = [Experiment.AGENT_SS.value, Experiment.AGENT_HHP.value, Experiment.AGENT_HHPD.value, Experiment.AGENT_HEQHP.value, Experiment.AGENT_HEQHPD.value],
                seed:int = 1000,
                board = [2,3],
                uuid = "",
                tag = ""):
        self.envs = envs
        self.agents = agents
        self.total_timesteps = total_timesteps
        self.board = board
        self.tag = tag

        self.path_main_results = os.path.join(os.path.dirname(__file__), results_dir)        
        
        self.path_results_experiments = "results-{}-{}-{}-{}-{}-{}-{}-{}{}".format(total_timesteps, n_steps, batch_size, n_epochs, entropy_min, learning_rate, seed, act_func, uuid)        
        self.path_results_experiments = os.path.join(self.path_main_results, self.path_results_experiments)                
        
        self.observations = observations
        self.representations = representations
        self.dobjective_leniency = []
        self.dentropies_linearity = []        
        self.maps = []                 

    def update_tiles(self, map, tiles, t):                        
        for tile in tiles:
            map[map == tile] = t       

    def calc_segments(self, segments):
        level_segments = segments
        
        level_segments = level_segments.replace("'", "").replace("[", "").replace("]", "")
        
        level_segments = level_segments.split()        
        level_segments = np.array(level_segments).astype(int)
        aux_segments = np.array(level_segments).astype(int)

        n_segments = len(level_segments)

        level_segments = calc_prob_dist(level_segments)
        
        entropy_level = entropy(np.arange(n_segments))

        segments_linearity = 0
        for k, v in level_segments.items():        
            segments_linearity += 1

        #segments_linearity = 2 * (n_segments - segments_linearity)
        segments_linearity = segments_linearity
        segments_repeated = self._counter_segments_repeated(aux_segments)
        return level_segments, n_segments, segments_linearity, entropy_level, segments_repeated        

    def build_map_zelda(self, map, entropies, index, segments):                
                
        leniency = 0
        
        locations = array_el_locations(map)    
        level_segments, n_segments, segments_linearity, entropy_level, segments_repeated = self.calc_segments(segments[index])

        n_elements = 0
        
        w = {zelda.Enemy.ID : 2, zelda.Key.ID : -0.5, zelda.Coin.ID : 2, zelda.Weapon.ID : -0.5, zelda.DoorExit.ID : -0.5}
        tiles = [zelda.Coin.ID, zelda.Key.ID, zelda.Enemy.ID, zelda.Weapon.ID, zelda.DoorExit.ID]
        
        for tile in tiles:                              
            n_elements += np.count_nonzero(map == tile) * w[tile]

        pos_player = locations[zelda.Player.ID]
        pos_player = pos_player[0]
        row, col   = pos_player[0], pos_player[1]

        #tiles = [2, 3, 4, 5, 6, 7, 8]
        tiles = [zelda.DoorEntrance.ID, zelda.DoorExit.ID, 
                 zelda.Coin.ID, zelda.Key.ID, 
                 zelda.Player.ID,
                 zelda.Enemy.ID, zelda.Weapon.ID]
        self.update_tiles(map, tiles, 0)

        h = 0 

        map, max_dist, ent, grounds = wave_front_entrace(map, row, col, h)   
        #self.show_map(map)

        map[row][col] = 50
        
        col, row = map.shape

        tiles = [zelda.DoorExit.ID, zelda.Coin.ID, zelda.Key.ID, zelda.Enemy.ID, zelda.Weapon.ID]
        #w = {zelda.DoorExit.ID : -0.5, zelda.Coin.ID : 2, zelda.Key.ID : -0.5, zelda.Enemy.ID : 2, zelda.Weapon.ID : -0.5}
        dist = 0
        for tile in tiles:
            for pos_tile in locations[tile]:
                row = pos_tile[0]
                col = pos_tile[1]                                
                if tile == zelda.DoorExit.ID or tile == zelda.Weapon.ID or tile == zelda.Key.ID:
                   dist += map[row][col]                         
                elif tile == zelda.Enemy.ID:
                   d_enemy = map[row][col]
                   d_enemy = (max_dist - d_enemy) + 1 #* math.pi
                   dist += d_enemy                                                      
                else:                   
                   dist += map[row][col]
                   
                map[row][col] = tile + 100

        segs = self.convert_segments(segments[index])
        leniency   = (dist * n_elements * entropy_level)#entropies[index])
        linearity = self.calc_linearity(segs, n_segments, entropy_level)
        #print("Dist {}, MaxDist {}, NElements {}, NSegments {}({}-{}), Leniency {}, Linearity {}, Entropy {} ".format(dist, max_dist, n_elements, n_segments, segments_linearity, segments_repeated, round(leniency,2), round(linearity,2), round(entropies[index],2) ))        
        return leniency , linearity, map

    def calc_linearity(self, segments, w1 = 1, w2 = 1):         
        linearity = ((self._reward_distance(segments)) * w1 * w2)        
        return linearity

    def show_map(self, map):            
        fig, ax = plt.subplots(figsize=(10,10))
        # Loop over data dimensions and create text annotations.
        for _i in range(len(map)):
            for _j in range(len(map[0])):
                text = ax.text(_j, _i, map[_i, _j],
                        ha="center", va="center", color="w")                           
        plt.tight_layout()
        plt.imshow(map)
        plt.show()
        plt.close()

    def convert_segments(self, segment):
        level_segments = segment                
        level_segments = level_segments.replace("'", "").replace("[", "").replace("]", "")        
        level_segments = level_segments.split()        
        level_segments = np.array(level_segments).astype(int)        
        segs = level_segments.reshape(self.board[0], self.board[1])        

        return segs

    def get_positions(self, tiles, map):        
        max_row = map.shape[0]
        max_col = map.shape[1]
        new_map = []
        for row in range(max_row):
            for col in range(max_col):
                id = int(map[row][col])
                if id in tiles:
                    new_map.append((row, col))
        return new_map

    def _counter_segments_repeated(self, segments):
        _map = np.array(segments)
        _map = list(_map.flatten())
        _map = collections.Counter(_map)
        counter = 0
        #print(_map)
        for e in _map.keys():    
            if _map[e] > 1:
                counter += _map[e]
        return counter      

    def _reward_distance(self, segments):
        
        map_segments = np.array(segments)
        n_segments = map_segments.shape[1] * map_segments.shape[0]      
        #print(n_segments)  
        map_segments = set(map_segments.flatten())            
        
        reward_e = 0

        for segment in map_segments:
            positions = self.get_positions([segment], segments)                        
            if len(positions) > 1:    
                pos_init = positions[0]
                for row, col in positions:                                        
                    reward_e += (euclidean_distance(pos_init, (row, col)))
                    #reward_e += (n_segments - manhattan_distance(pos_init, (row, col)))

        return reward_e

    def build_map_mazecoin(self, map, entropies, index, segments):
       
        map = np.array(map)

        locations = array_el_locations(map)            
        level_segments, n_segments, segments_linearity, entropy_level,segments_repeated = self.calc_segments(segments[index])     
        
        #Calcula a distância entre as moedas
        map_coin = map.copy()
        pos_coin = locations[mazecoin.CoinGold.ID]        
        pos_coin = pos_coin[0]
        row_coin, col_coin = pos_coin[0], pos_coin[1]
        self.update_tiles(map_coin, [mazecoin.CoinGold.ID, mazecoin.Player.ID], 0)
        h = 0 
        map_coin, max_dist, ent, grounds = wave_front_entrace(map_coin, row_coin, col_coin, h)                       
        map_coin[row_coin][col_coin] = 50

        tiles = [2]        
        for tile in tiles:   
            for pos_tile in locations[tile]:
                row = pos_tile[0]
                col = pos_tile[1]
                if row_coin != row and col_coin != col:                    
                    map_coin[row][col] = tile + 100

        n_elements = 0        
        tiles = [mazecoin.CoinGold.ID]#, mazecoin.Ground.ID, mazecoin.Block.ID]
        w = {mazecoin.CoinGold.ID : 2}#, mazecoin.Ground.ID : -1, mazecoin.Block.ID : 1}
        for tile in tiles:                                                       
            n_elements += np.count_nonzero(map == tile) * w[tile]           

        pos_player = locations[mazecoin.Player.ID]            
        pos_player = pos_player[0]    
        row, col   = pos_player[0], pos_player[1]         
        
        self.update_tiles(map, [mazecoin.CoinGold.ID, mazecoin.Player.ID], 0)
        
        h = 0 
        map, max_dist, ent, grounds = wave_front_entrace(map.copy(), row, col, h)

        map[row][col] = 50
        linearity     = 0

        dist = 0        
        tiles = [2]
        w = {mazecoin.CoinGold.ID : 2, mazecoin.Player.ID : 1} #, mazecoin.Ground.ID : 0.1, mazecoin.Block.ID : 2}

        ws = {6 : 0, 5 : 0.9, 4: 0.7, 3 : 0.5, 2 : 0.3, 1: 0.2, 0 : 0.1  }

        for tile in tiles:
            for pos_tile in locations[tile]:
                row = pos_tile[0]
                col = pos_tile[1]
                dist += map[row][col] #* w[tile]               
                map[row][col] = tile + 100        

        #leniency = (dist * entropies[index]) * (segments_linearity / n_segments) 
        
        segs = self.convert_segments(segments[index])        

        leniency   = (dist * n_elements * entropy_level) #entropies[index])
        linearity = self.calc_linearity(segs, n_segments, entropy_level)
        #print("Dist {}, MaxDist {}, NElements {}, NSegments {}({}-{}), Leniency {}, Linearity {}, Entropy {} ".format(dist, max_dist, n_elements, n_segments, segments_linearity, segments_repeated, round(leniency,2), round(linearity,2), round(entropies[index],2) ))
        return leniency, linearity, map

    def prepare(self):
        timesteps = [self.total_timesteps]    
        mlp_units = [64] 
        n_experiments   = 1
        RL_ALG          = "PPO"        
        self.envs = [Game.ZELDA.value, Game.ZELDALOWMAPS.value, Game.MAZECOINLOWMAPS.value]
        #self.envs = [Game.ZELDA.value, Game.MAZECOINLOWMAPS.value]
        #self.envs = [Game.ZELDALOWMAPS.value]
        #self.envs = [Game.ZELDA.value, Game.MAZECOINLOWMAPS.value]
        for version in self.agents:
        
            for t_time_s in timesteps:
                
                interation_path = t_time_s
                print()
                print()
                for mlp_u in mlp_units:                       
                    
                    for _rep in self.representations:
                        
                        for _obs in self.observations:                                
                                
                            for par in range(n_experiments): 

                                for env_game in self.envs:

                                    self.dobjective_leniency = []
                                    self.dentropies_linearity = []        
                                    self.maps = []                                        
                                
                                    path_results = os.path.join(self.path_results_experiments, version)
                                    main_dir = "{}-{}-{}-{}".format("Experiment 0" + str(par+1),version, env_game, RL_ALG)  
                                
                                    path_experiments = os.path.join(path_results, main_dir)

                                    path_observation = os.path.join(path_experiments, _rep+"-"+_obs)    
                                    path_map_best = os.path.join(path_observation, "map/best/")

                                    path_info = os.path.join(path_observation, "Info.csv")

                                    paths_maps = [path_map_best]

                                    entropies = []
                                    df        = pd.read_csv(path_info)
                                    data      = df["entropy"]
                                    entropies = np.array(data).astype("float")  
                                    data      = df["segments"] 
                                    segments  = np.array(data)
                                    index     = 0                                                 

                                    for path_map in paths_maps:
                                        files = os.listdir(path_map)
                                        #files.sort()
                                        #print(files)
                                        #time.sleep(5)
                                        for file in files:                                                    
                                                map = []
                                                if file[-3:] in {'csv'}:
                                                    file_name = "Map{}.csv".format(index+1)
                                                    pathfile = os.path.join(path_map, file_name)          
                                                    with open(pathfile, newline='') as csvfile:
                                                        data = list(csv.reader(csvfile))            
                                                        
                                                    map = np.array(data).astype("int")  
                                                    locations = array_el_locations(map)                                                
                                                    
                                                    if (env_game == Game.MAZECOINLOWMAPS.value):
                                                        leniency, linearity, map    = self.build_map_mazecoin(map, entropies, index, segments)                                                        
                                                    if (env_game == Game.ZELDA.value):
                                                        leniency, linearity, map    = self.build_map_zelda(map, entropies, index, segments)                                                        
                                                    if (env_game == Game.ZELDALOWMAPS.value):
                                                        leniency, linearity, map    = self.build_map_zelda(map, entropies, index, segments)                                                        

                                                    self.maps.append(map)
                                                                                                        
                                                    self.dobjective_leniency.append(round(leniency, 2))
                                                    self.dentropies_linearity.append(round(linearity, 2))
                                                    index += 1                                                  

                                    self.gera_graficos(self.path_results_experiments, env_game, version, entropies, segments)

    def diversity(self):
        timesteps = [self.total_timesteps]    
        mlp_units = [64] 
        n_experiments   = 1
        RL_ALG          = "PPO"        
        #self.envs = [Game.ZELDA.value, Game.MAZECOINLOWMAPS.value]
        for version in self.agents:
        
            for t_time_s in timesteps:
                
                interation_path = t_time_s
                print()
                print()
                for mlp_u in mlp_units:                       
                    
                    for _rep in self.representations:
                        
                        for _obs in self.observations:                                
                                
                            for par in range(n_experiments): 

                                for env_game in self.envs:
                                    
                                    
                                    self.dobjective_leniency = []
                                    self.dentropies_linearity = []        
                                    self.maps = []                                        
                                
                                    path_results = os.path.join(self.path_results_experiments, version)
                                    main_dir = "{}-{}-{}-{}".format("Experiment 0" + str(par+1),version, env_game, RL_ALG)  
                                
                                    path_experiments = os.path.join(path_results, main_dir)

                                    path_observation = os.path.join(path_experiments, _rep+"-"+_obs)    
                                    path_map_best = os.path.join(path_observation, "map/best/")

                                    path_info = os.path.join(path_observation, "Info.csv")

                                    paths_maps = [path_map_best]

                                    entropies = []
                                    df        = pd.read_csv(path_info)
                                    data      = df["entropy"]
                                    entropies = np.array(data).astype("float")  
                                    data      = df["segments"] 
                                    segments  = np.array(data)
                                    index     = 0                                                 
                                    x = []
                                    for path_map in paths_maps:
                                        
                                        data = []
                                        for file in os.listdir(path_map):    
                                                map = []
                                                if file[-3:] in {'csv'}:
                                                    pathfile = os.path.join(path_map, file)                                                             
                                                    js_sum = 0.001                                                    
                                                    generatorA = Generator(path=pathfile, piece_size=(8, 8), loadmap=True, border=True)
                                                    yy, xx = [], []
                                                    indexpiece = 0
                                                    for m in range(generatorA.count()-1, 0, -1):
                                                        p = calcTileProb(generatorA.get_piece(m))                                                                
                                                        pp = generatorA.get_piece(m)  
                                                        for n in range(generatorA.count()):
                                                            if (m != n):
                                                                qq = generatorA.get_piece(n)                                                         
                                                                q = calcTileProb(generatorA.get_piece(n))
                                                                indexpiece += 1
                                                                xx.append(indexpiece)
                                                                js = calKLFromMap(p, q) 
                                                                yy.append(js)            
                                                                js_sum += js                                                    
                                                    index += 1
                                                    x.append(index) 
                                                #print(js_sum)
                                                data.append(js_sum)
                                        print()                                        
                                        """
                                        fig, axs = plt.subplots()
                                        plt.plot(xx, yy)
                                        plt.xlabel('Index')
                                        plt.ylabel('Diversity')                                                                                            
                                        plt.title(file)
                                        plt.show()
                                        plt.close()  
                                        """

                                        path = self.path_results_experiments

                                        save_file = mk_dir(path, "Expressive Range")
                                        
                                        data = np.array(data)
                                        #data.sort()
                                        normalized =  normalize(data)
                                        print(normalized)
                                        fig, axs = plt.subplots()
                                        bins = int( len(normalized) * 0.15)

                                        #nbins = len(normalized)
                                        #histogram, bins = np.histogram(normalized, bins=nbins)
                                        #pdf = (histogram / (sum(histogram)))
                                        #bin_centers = (bins[1:] + bins[:-1]) * 0.5

                                        #_data = []

                                        #_data.append(normalized)                                        
                                        #axs.boxplot(_data)        
                                        #axs.violinplot(_data)

                                        axs.hist(normalized, bins, density=True, histtype='barstacked', rwidth=0.8)
                                        fig.tight_layout()                                        
                                        plt.title("{} - {}".format(version, env_game))
                                        plt.xlabel('Diversidade', fontsize=16)
                                        #plt.ylabel('Leniência', fontsize=16)
                                        
                                        plt.xticks(fontsize=16)
                                        plt.yticks(fontsize=16)        
                                        
                                        #print("Salvando o arquivo em: {}".format(save_file))                                        
                                        plt.savefig(os.path.join(save_file, "{}-{}-{}{}".format(env_game, version, "Diversity", ".pdf") ))
                                        #plt.show()
                                        plt.close()        

                                        fig, axs = plt.subplots()
                                        plt.plot(x, data)
                                        plt.xlabel('Index')
                                        plt.ylabel('Diversity')                                        
                                        plt.savefig(os.path.join(save_file, "{}-{}-{}{}".format(env_game, version, "Diversity-plot", ".pdf") ))
                                        #plt.show()
                                        plt.close()                                                                                                                   
    
    def reward_neighbors(self, segments):
        
        n, m = segments.shape
        map_segments = np.array(segments)        
        map_segments = list(map_segments.flatten())                    
        positions = self.get_positions(map_segments, segments)

        reward = 0

        for row, col in positions:
            segment = segments[row][col]
            nei = neighbors(row, col, n-1, m-1)                        
            for r, c in nei:                
                if (segments[r][c] != -1) and segments[r][c] == segment and (row != r or col != c):
                    reward += -2

        return reward
    
    def gera_graficos(self, path, env_game, agent, entropies, segments):

        #Normalized Data
        dobjective_leniency = normalize(np.array(self.dobjective_leniency))
        dentropies_linearity = normalize(np.array(self.dentropies_linearity))       

        maps_id = np.arange(0, len(dobjective_leniency))

        #a = np.asarray([ maps_id, dobjective_leniency, dentropies_linearity ])
        
        save_file = mk_dir(path, "Expressive Range")
        save_file = os.path.join(save_file, "{}-{}-{}-{}".format("ExpressiveRange", env_game, agent, ".csv") )

        #numpy.savetxt(save_file, a, delimiter=",")

        df =pd.DataFrame({'Linearity' : dentropies_linearity, 'Leniency': dobjective_leniency}) 
        df.to_csv(save_file)

        save_map = False
        rewards_nei = []
        for m in range(len(self.maps)):    

            if save_map:
                fig, ax = plt.subplots(figsize=(10,10))
                # Loop over data dimensions and create text annotations.
                for _i in range(len(self.maps[m])):
                    for _j in range(len(self.maps[m][0])):
                        text = ax.text(_j, _i, self.maps[m][_i, _j],
                                ha="center", va="center", color="w")        
                    title = "Linearidade: {}, Entropy: {}, Leniency: {}, Segments {}".format(round(dentropies_linearity[m],2), 
                                                                               round(entropies[m], 2), 
                                                                               round(dobjective_leniency[m],2),
                                                                               segments[m])                            
            segs = self.convert_segments(segments[m])
            rewards_nei.append(self._reward_distance(segs))# self.reward_neighbors(segs))
            #rewards_nei.append(self.reward_neighbors(segs)*-1)
            #rewards_nei.append( (self.reward_neighbors(segs)*-1)+self._reward_distance(segs) )
            
            #print (title)
            if save_map:
                plt.tight_layout() 
                plt.title(title)
                plt.imshow(self.maps[m])
                save_file = mk_dir(path, "mapcolors")      
                save_file = mk_dir(save_file, agent)
                path_save_file = mk_dir(save_file, env_game)
                save_file = os.path.join(path_save_file, "{}{}".format("Map"+str(m), ".png") )
                plt.savefig(save_file)
                plt.close()

                #df = pad.DataFrame(self.maps[m])
                #path_csv_file = mk_dir(path_save_file, "csv")
                #if (self._reward > 0):
                #df.to_csv(path_csv_file + "/map"+str(m)+".csv", header=False, index=False)

        #cmap     = 'Greens_r' #'Spectral' 'inferno'
        #cmap='inferno'
        if self.tag == "":
            cmap='inferno'
            #cmap='ocean_r'
            #cmap='ocean11'
        elif self.tag == "reward_neighbors":
            cmap = 'Greens_r'
        elif self.tag == "reward_neighbors_reward_distance":
            cmap = 'Spectral'
        elif self.tag == "-V2":
            cmap='Pastel1'
        elif self.tag == "reward_neighbors-V2":
            cmap = 'Set1'
        elif self.tag == "reward_neighbors_reward_distance-V2":
            cmap = 'Accent'

        mincnt   = 0
        gridsize = 10                  

        dentropies_linearity = np.array(dentropies_linearity)

        xlim = dobjective_leniency.min(), dobjective_leniency.max()
        ylim = dentropies_linearity.min(), dentropies_linearity.max()

        fig, ax0 = plt.subplots(sharey=True)
        
        hb = ax0.hexbin(dentropies_linearity, dobjective_leniency, gridsize=gridsize, cmap=cmap, mincnt=mincnt)
        ax0.set(xlim=xlim, ylim=ylim)
        #ax0.set_title("Hexagon binning")
        #cb = fig.colorbar(hb, ax=ax0, label='Número de Níveis')
        cb = fig.colorbar(hb, ax=ax0, label='Number of Levels')
        cb.ax.tick_params(labelsize=16)        

        save_file = mk_dir(path, "mapcolors")
        plt.tight_layout()
        #plt.xlabel('Linearidade', fontsize=16)
        #plt.ylabel('Leniência', fontsize=16)
        plt.xlabel('Linearity', fontsize=16)
        plt.ylabel('Leniency', fontsize=16)        
        
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=16)        
        plt.tight_layout()
        print("Salvando o arquivo em: {}".format(save_file))
        #plt.savefig(os.path.join(save_file, "{}-{}-{}{}".format(env_game, agent, "Leniency-Linearity", ".png") ))
        plt.savefig(os.path.join(save_file, "{}-{}-{}{}{}".format(env_game, agent, "Leniency-Linearity", self.tag, ".pdf") ))
        #plt.show()
        plt.close()                

        """
        fig, ax0 = plt.subplots(sharey=True)

        data = []
        
        rewards_nei =  np.array(rewards_nei)
        print(rewards_nei)
        rewards_nei_normalize = normalize(rewards_nei)
        
        #data.append(rewards_nei_normalize)        
        #ax0.boxplot(data)        
        #ax0.violinplot(data)
        #ax0.set_xticklabels(['Reward neighbors'], fontsize=16)
        
        ax0.hist(rewards_nei_normalize, color='g')             
        ax0.set_ylabel('Frequência')
        ax0.set_xlabel('Neighbors')         
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=16)
        plt.tight_layout()
        #plt.savefig(os.path.join(save_file, "{}-{}-{}{}".format(env_game, agent, "Leniency-Linearity-Boxplot", ".png") ))
        plt.savefig(os.path.join(save_file, "{}-{}-{}{}{}".format(env_game, agent, "Reward_neighbors-Boxplot", self.tag, ".pdf") ))        
        #plt.show()
        plt.close() 



        fig, ax0 = plt.subplots(sharey=True)

        data = []

        data.append(dobjective_leniency)
        data.append(dentropies_linearity)
        ax0.boxplot(data)        
        ax0.violinplot(data)
        #ax0.set_xlabel("Expressive Range", fontsize=18)   
        #ax0.set_ylabel("Expressive Range", fontsize=18)   
        ax0.set_xticklabels(['Leniência','Linearidade'], fontsize=16)
        
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=16)
        plt.tight_layout()
        #plt.savefig(os.path.join(save_file, "{}-{}-{}{}".format(env_game, agent, "Leniency-Linearity-Boxplot", ".png") ))
        plt.savefig(os.path.join(save_file, "{}-{}-{}{}{}".format(env_game, agent, "Leniency-Linearity-Boxplot", self.tag, ".pdf") ))        
        #plt.show()
        plt.close() 

        fig, ax = plt.subplots(sharey=True)
        ax.hist(dobjective_leniency, color='g')             
        ax.set_ylabel('Frequência')
        ax.set_xlabel('Leniência') 
        plt.tight_layout()
        plt.savefig(os.path.join(save_file, "{}-{}-{}{}{}".format(env_game, agent, "Leniency-Hist", self.tag, ".pdf") ))               
        #plt.show()
        plt.close()               

        fig, ax = plt.subplots(sharey=True)
        ax.hist(dentropies_linearity, color='g')             
        ax.set_ylabel('Frequência')
        ax.set_xlabel('Linearidade')        
        plt.tight_layout()
        plt.savefig(os.path.join(save_file, "{}-{}-{}{}{}".format(env_game, agent, "Linearity-Hist", self.tag, ".pdf") ))                       
        #plt.show()
        plt.close()

        fig, axs = plt.subplots()
        bins = 100 #int( len(dentropies_linearity) * 0.15)
        #dentropies_linearity, dobjective_leniency

        axs.hist(dobjective_leniency, bins, density=True, histtype='barstacked', rwidth=0.8)
        
        fig.tight_layout()                                               
        
        plt.ylabel('Frequência', fontsize=16)
        plt.xlabel('Leniência', fontsize=16)
        #ax.set_ylabel('Frequência')
        #ax.set_xlabel('Linearidade')                
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=16)        
        
        #print("Salvando o arquivo em: {}".format(save_file))                                        
        plt.savefig(os.path.join(save_file, "{}-{}-{}{}{}".format(env_game, agent, "Leniency-Hist-barstacked", self.tag, ".pdf") ))
        #plt.show()
        plt.close()          
        """

def gera_graficos_expressive_range(results_dir = "./results/",
                            total_timesteps = 50000,              
                            learning_rate: float = 2.5e-4, 
                            n_steps:int   = 128,                                                        
                            batch_size:int = 64,
                            n_epochs:int = 10,                                          
                            act_func = ActivationFunc.SIGMOID.value,
                            entropy_min:int = 1.80,                            
                            envs = [Game.ZELDA.value, Game.MINIMAP.value, Game.MAZECOIN.value, Game.MAZE.value, Game.DUNGEON.value],
                            representations = [Behaviors.NARROW_PUZZLE.value, Behaviors.WIDE_PUZZLE.value],
                            observations = [WrappersType.MAP.value],              
                            agents  = [Experiment.AGENT_SS.value, Experiment.AGENT_HHP.value, Experiment.AGENT_HHPD.value, Experiment.AGENT_HEQHP.value, Experiment.AGENT_HEQHPD.value],
                            seed:int = 1000,    
                            board = [2,3],                         
                            uuid = "",
                            tag  = ""):
    expressiveRange = ExpressiveRangePlot(results_dir = results_dir,
                                        total_timesteps = total_timesteps,
                                        learning_rate   = learning_rate,        
                                        n_steps         = n_steps,                                                                                    
                                        batch_size      = batch_size,
                                        n_epochs        = n_epochs,
                                        act_func        = act_func,
                                        entropy_min     = entropy_min,
                                        envs            = envs,
                                        agents           = agents,                                            
                                        representations = representations,      
                                        observations    = observations,
                                        seed            = seed,
                                        board           = board,
                                        uuid            = uuid,
                                        tag             = tag)

    expressiveRange.prepare()
