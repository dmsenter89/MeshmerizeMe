
"""Python module to find equally spaced points on an SVG path."""

import svgpathtools
from numpy import linspace
import numpy as np
from . import meshmerizeme_logger as logger
from tqdm import tqdm
import time
from multiprocess import Process, Array, Value, Manager
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Default config settings which users can override via CLI arguments.
USER_CONFIG = {
    "path" : None,
    "ds" : None,
    "min_T" : 0,
    "max_T" : 1,
    "point_params" : None,
    "subpath_length" : 25,
    "num_points" : None,
    "learning_rate" : 0.00005,
    "max_iter" : 50,
    "threshold" : 1e-6,
    "show_graph" : False,
    "num_parallel_processes" : 10
}

def get_point_coords(path, point_params):
    return np.asarray([ path.point(T) for T in point_params ])

def get_segment_lengths(point_coords):
    return np.abs( point_coords[1:] - point_coords[:-1] )

def get_mean_squared_relative_error(segment_lengths, ds):
    return np.mean( np.square( (segment_lengths - ds) / ds ) )

def graph_point_params_and_mse(args):
    def get_point_coords(path, point_params):
        coords = [ path.point(T) for T in point_params ]
        x = [coord.real for coord in coords]
        y = [coord.imag for coord in coords]
        coords = [ (x[i], y[i]) for i in range(len(coords)) ]
        return coords

    if args["show_graph"] is False:
        return
    fig = plt.figure()
    
    ax1 = fig.add_subplot(3,1,1)
    num_bins = len( args["point_params"] ) * 2
    ax1.set_title("Density of Point Params")
    ax1.set_xlabel("Point Params T")
    ax1.set_ylabel("Frequency")
    hist, bins = np.histogram( args["point_params"], bins=num_bins )
    ax1_artist = ax1.bar(bins[:-1], hist, width=np.ptp(args["point_params"]) / num_bins )
    
    ax2 = fig.add_subplot(3,1,2)
    ax2.set_title("MSE of Distances Between Points")
    ax2.set_xlabel("No. of Gradient Descent Iterations.")
    ax2.set_ylabel("MSE")
    ax2_artist = ax2.plot(args["iters"], args["costs"])[0]

    ax3 = fig.add_subplot(3,1,3)
    ax3.set_title("Points on Path")
    ax3.set_xlabel("X Coord.")
    ax3.set_ylabel("Y Coord.")
    point_coords = get_point_coords( args["path"], args["point_params"] )
    x = [ point_coord[0] for point_coord in point_coords ]
    y = [ point_coord[1] for point_coord in point_coords ]
    ax3_artist = ax3.scatter(x, y)
    
    plt.tight_layout()

    def animate(i):
        hist, bins = np.histogram( args["point_params"], bins=num_bins )
        [bar.set_height(hist[i]) for i, bar in enumerate(ax1_artist)]        
        [bar.set_x(bins[i]) for i, bar in enumerate(ax1_artist)]
        ax1.relim()
        ax1.autoscale_view()

        ax2_artist.set_data(args["iters"], args["costs"])
        ax2.relim()
        ax2.autoscale()

        point_coords = get_point_coords( args["path"], args["point_params"] )
        ax3_artist.set_offsets(point_coords)
        ax3.autoscale_view()

        plt.draw()
    ani = animation.FuncAnimation(fig, animate, interval=1000)
    plt.show()



class PointsEstimator():
    """Finds estimates for equally spaced points on an SVG path."""
    def __init__(self, config=USER_CONFIG):
        """
        Args:
            path: An svgpathtools Path object.
            ds: Desired spacing of points.
            min_T: Parameter 0<=T<=1 for the starting point of a segment on the path.
            max_T: Parameter 0<=T<=1 for the ending point of a segment on the path.
        """
        self.path = config["path"]
        self.ds = config["ds"]
        self.min_T = config["min_T"]
        self.max_T = config["max_T"]

class GradientDescentEstimator(PointsEstimator):
    """
    Uses gradient descent to minimize the relative error of distances between points.
    First, the path is split into multiple segments which are estimated in parallel.
    Then, the resulting points are used as initial estimates for the final aggregate minimization.    
    """
    def __init__(self, config=USER_CONFIG):
        """
        Args: (See also the PointsEstimator class)
            point_params: T parameters for initial estimates of points.
            subpath_length: Length of subpaths to estimate in parallel in terms of ds.
            num_points: Number of points to fit to the path. This overrides the point_params
                        argument with a list of equally spaced point parameters T.
            learning_rate: The learning rate used by the gradient descent algorithm for the
                           final aggregate minimization over the entire path.
            max_iter: Maximum number of gradient descent iterations for the final aggregate
                      minimization over the entire path.
            threshold: Stop the gradient descent process if the mean squared error
                       of point distances converges within the threshold.
            show_graph: Flag to display/hide real-time graphs (for the final aggregate minimization) containing:
                            -Histogram of point parameters T.
                            -Mean squared error of point distances.
                            -Plot of the estimated points.
            num_parallel_processes: Number of processes to estimate subpaths in parallel.
        """
        super().__init__(config)
        self.subpath_length = config["subpath_length"] * self.ds
        self.learning_rate = config["learning_rate"]
        self.max_iter = config["max_iter"]
        self.threshold = config["threshold"]
        self.show_graph = config["show_graph"]
        self.num_parallel_processes = config["num_parallel_processes"]
        self.num_subpaths = int( self.path.length() / self.subpath_length )
        
        if config["num_points"] is not None:
            self.num_points = config["num_points"]
            self.num_segments = self.num_points - 1
            self.point_params = np.linspace(self.min_T, self.max_T, self.num_points)                
        else:
            if config["point_params"] is not None:
                self.num_points = len(config["point_params"])
                self.num_segments = self.num_points - 1
                self.point_params = config["point_params"]
            else:
                self.num_segments = int( np.ceil( self.path.length(T0=self.min_T, T1=self.max_T) / self.ds ) )
                self.num_points = self.num_segments + 1
                self.point_params = np.linspace(self.min_T, self.max_T, self.num_points)                


    def get_mse_gradient(self):
        point_coords = get_point_coords(self.path, self.point_params)
        segment_lengths = get_segment_lengths(point_coords)
        segment_vectors = point_coords[1:] - point_coords[:-1]
        segment_vectors = np.stack((segment_vectors.real, segment_vectors.imag), -1)
        path_derivatives = np.asarray([ self.path.derivative(T) for T in self.point_params ])
        path_derivatives = np.stack((path_derivatives.real, path_derivatives.imag), -1)
        gradient = np.zeros(self.num_points)

        gradient_term_1 = np.clip( (segment_lengths - self.ds) * np.power(segment_lengths, -1), -99999, 99999)
        gradient_term_2 = np.asarray([ np.dot( segment_vectors[i], path_derivatives[i+1] ) for i in range(self.num_segments) ])
        gradient_term_3 = np.asarray([ np.dot( segment_vectors[i], path_derivatives[i] ) for i in range(self.num_segments) ])

        gradient[1:] += gradient_term_1 * gradient_term_2
        gradient[:-1] -= gradient_term_1 * gradient_term_3
        gradient /= self.num_segments * ( self.ds ** 2 )

        return gradient

    def init_graph_args(self, init_mse):
        shared_point_params = Array("d", self.point_params)
        iters = Array("i", [i - 50 for i in range(50)])
        costs = Array("d", [init_mse] * 50)
        self.graph_args = {
            "path" : self.path,
            "show_graph" : self.show_graph,
            "point_params" : shared_point_params,
            "iters" : iters,
            "costs" : costs
        }

    def update_graph_args(self, new_mse):
        self.graph_args["iters"][:-1] = self.graph_args["iters"][1:]
        self.graph_args["iters"][-1] += 1
        self.graph_args["costs"][:-1] = self.graph_args["costs"][1:]
        self.graph_args["costs"][-1] = new_mse
        self.graph_args["point_params"][:] = self.point_params

    def fit_subpath(self):  
        cur_iter = 0
        point_coords = get_point_coords(self.path, self.point_params)
        segment_lengths = get_segment_lengths(point_coords)
        mse = get_mean_squared_relative_error(segment_lengths, self.ds)
        mse_difference = 1

        self.init_graph_args(mse)
        p = Process(target=graph_point_params_and_mse, args=(self.graph_args,))
        p.start()

        while np.abs(mse_difference) > self.threshold and cur_iter < self.max_iter:
            cur_iter += 1
            mse_gradient = self.get_mse_gradient()
            self.point_params -= self.learning_rate * mse_gradient
            self.point_params = np.clip( self.point_params , self.min_T, self.max_T )
            point_coords = get_point_coords(self.path, self.point_params)
            segment_lengths = get_segment_lengths(point_coords)
            new_mse = get_mean_squared_relative_error(segment_lengths, self.ds)
            mse_difference = mse - new_mse
            mse = new_mse
            self.update_graph_args(new_mse)
        p.join()
        p.terminate()

        return np.unique(self.point_params)

    def fit_subpaths_in_parallel(self, cur_subpath_index, point_params, config):        
        while cur_subpath_index.value < self.num_subpaths:
            subpath_index = cur_subpath_index.value
            cur_subpath_index.value = subpath_index + 1

            subpath_estimator_config = config
            subpath_estimator_config["min_T"] = self.subpath_boundary_points[subpath_index]
            subpath_estimator_config["max_T"] = self.subpath_boundary_points[subpath_index+1]
            subpath_estimator_config["num_points"] = None
            subpath_estimator_config["show_graph"] = False
            subpath_estimator_config["learning_rate"] = 0.0000005
            subpath_estimator_config["max_iter"] = 500

            subpath_estimator = GradientDescentEstimator(subpath_estimator_config)
            subpath_params = subpath_estimator.fit_subpath()
            if subpath_index < self.num_subpaths - 1:
                subpath_params = subpath_params[:-1] # Remove last point so it is not included twice.
            point_params.extend( subpath_params ) 

    def log_subpath_progress(self, cur_subpath_index):
        last_logged_subpath_index = 0
        next_subpath_index_to_log = cur_subpath_index.value
        with tqdm(total=self.num_subpaths, desc="Subpaths") as progress_bar:
            while next_subpath_index_to_log < self.num_subpaths and last_logged_subpath_index < self.num_subpaths:
                progress_bar.update(next_subpath_index_to_log - last_logged_subpath_index)
                last_logged_subpath_index = next_subpath_index_to_log
                next_subpath_index_to_log = cur_subpath_index.value
                time.sleep(0.1)
            progress_bar.update(self.num_subpaths - last_logged_subpath_index)
    
    def fit_path(self):
        self.subpath_boundary_points = [0]
        for i in range(self.num_subpaths-1):
            self.subpath_boundary_points.append( self.path.ilength((i+1) * self.subpath_length) )
        self.subpath_boundary_points.append(1)

        with Manager() as manager:
            cur_subpath_index = Value("i", 0)
            shared_point_params = manager.list()
            parallel_processes = []
            for i in range(self.num_parallel_processes):
                p = Process(target=self.fit_subpaths_in_parallel, args=(cur_subpath_index, shared_point_params, USER_CONFIG.copy()))
                parallel_processes.append(p)
                p.start()
            progress_bar_process = Process(target=self.log_subpath_progress, args=(cur_subpath_index,))
            parallel_processes.append(progress_bar_process)
            progress_bar_process.start()
            for p in parallel_processes:
                p.join()
            for p in parallel_processes:
                p.terminate()
            self.point_params = shared_point_params[:]
        self.point_params.sort()
        if len(self.point_params) > self.num_points: # Too many points
            self.point_params = self.point_params[:self.num_points]
        elif len(self.point_params) < self.num_points: # Too few points
            num_new_points = self.num_points - len(self.point_params)
            self.point_params.extend( np.random.uniform(self.min_T, self.max_T, num_new_points) )
            self.point_params.sort()
        self.point_params = np.asarray(self.point_params)
        self.point_params = self.fit_subpath()

        return self.point_params

