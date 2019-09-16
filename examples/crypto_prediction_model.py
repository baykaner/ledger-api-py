# ------------------------------------------------------------------------------
#
#   Copyright 2018-2019 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------
from typing import List
import base64

from fetchai.ledger.api import LedgerApi
from fetchai.ledger.contract import SmartContract
from fetchai.ledger.crypto import Entity, Address

GRAPH_FILE_NAME = "/Users/khan/fetch/models/crypto_price_prediction/bitcoin_price_prediction_graph.bin"

EXAMPLE_INPUT_HISTORICS = "430.573, 428.26, 428.26, 428.26, 428.26, 428.26, 428.26, 428.26, 428.26, 428.26, 428.26, 428.26, 428.26, 428.26, 430.804, 430.804, 430.804, 430.804, 430.804, 430.804, 430.804, 430.804, 430.804, 430.804, 430.804, 430.804, 430.804, 430.804, 430.804, 430.804, 430.804, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 433.01, 433.01, 433.01, 433.01, 432.14, 432.14, 432.14, 432.14, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 433.01, 430.9, 430.9, 430.9, 430.9, 430.9, 430.9, 430.9, 430.9, 430.9, 430.9, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 432.62, 432.62, 432.62, 432.62, 432.62, 432.62, 432.62, 432.62, 432.62, 432.62, 432.62, 432.62, 432.62, 432.62, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 431.76, 432.62, 432.62, 432.62, 432.62, 432.62, 432.62, 432.62, 432.62, 432.62, 431.76, 431.76, 431.76, 431.75, 431.75, 431.75, 431.75, 431.75, 431.75, 431.75, 429.12, 429.12, 429.12, 429.12, 429.12, 429.12, 429.12, 429.12, 429.12, 429.12, 429.12, 429.12, 429.12, 429.12, 429.12, 431, 431, 431, 431, 431, 431, 431, 431, 431, 432.62, 432.62, 432.62, 432.62, 432.62, 432.62, 432.62, 432.62, 432.62, 428.27, 428.27, 428.27, 428.27, 428.27, 428.27, 428.27, 428.27, 428.27, 428.27, 428.27, 434.07, 434.07, 428.5, 434.07, 434.07, 434.07, 434.07, 434.07, 434.07, 434.07, 434.07, 434.07, 434.07, 434.07, 434.07, 428.6, 428.6, 428.6, 428.6, 428.6, 428.6, 428.6, 432.07, 432.07, 432.07, 432.07, 432.07, 432.07, 432.07, 432.07, 432.07, 432.07, 432.07, 432.07, 432.07, 432.07, 432.07"
EXAMPLE_LABEL_HISTORICS = "10328.3, 10320.0, 10320.0, 10322.0, 10325.0, 10325.0, 10325.0, 10325.8, 10325.8, 10326.6, 10326.6, 10326.9, 10326.9, 10321.0, 10321.0, 10321.1, 10315.3, 10315.2, 10315.2, 10315.0, 10315.0, 10316.8, 10319.2, 10319.2, 10319.2, 10321.1, 10322.6, 10335.0, 10339.6, 10345.0, 10345.8, 10341.9"

CONTRACT_TEXT = """

persistent graph_state : Graph;
persistent dataloader_state : DataLoader;
persistent optimiser_state : Optimiser;
persistent historics_state : Tensor;
persistent prediction_state : Tensor;
persistent scaler_state : Scaler;

// Smart contract initialisation sets up our graph, dataloader, and optimiser
// in this example we hard-code some values such as the expected input data size
// we could, however, easily add new methods that overwrite these values and 
// update the dataloader/optimiser as necessary
@init
function setup(owner : Address)

  use graph_state;
  use dataloader_state;
  use optimiser_state;
  use historics_state;
  use scaler_state;

  var owner_balance = State<UInt64>(owner);
  owner_balance.set(1000000u64);

  // initial graph construction
  var g = graph_state.get(Graph());
  graphSetup(g);
  graph_state.set(g);
  
  // initial dataloader construction
  var dl = dataloader_state.get(DataLoader("tensor"));
  dataloader_state.set(dl);
  
  // initial optimiser setup
  var optimiser = optimiser_state.get(Optimiser("sgd", g, dl, "Input", "Label", "Error"));
  optimiser_state.set(optimiser);
  
  // intial historics setup
  var tensor_shape = Array<UInt64>(3);
  tensor_shape[0] = 1u64;                 // data points are spot price, so size == 1
  tensor_shape[1] = 256u64;              // previous 256 data points
  tensor_shape[2] = 1u64;                 // batch size == 1
  var historics = historics_state.get(Tensor(tensor_shape));
  historics_state.set(historics);
  
  // initial scaler setup
  var scaler = Scaler();
  scaler_state.set(scaler);
  
endfunction

// Method initial graph setup (we could forgo adding ops/layers
// if the graph would later be set via a call to updateGraph)
@query
function graphSetup(g : Graph)
    // set up a trivial graph
    g.addPlaceholder("Input");
    g.addPlaceholder("Label");
    g.addRelu("Output", "Input");
    g.addMeanSquareErrorLoss("Error", "Output", "Label");
endfunction

// Method to update scaler settings
@action
function setScale(min_val : UInt64, max_val : UInt64)
    use scaler_state;
    var scaler = scaler_state.get();
    scaler.setScale(toFixed64(min_val), toFixed64(max_val));
    scaler_state.set(scaler);
endfunction

// Method to set new historics as data changes
@action
function setHistorics(new_historics: String)
    use graph_state;
    use historics_state;
    use prediction_state;
    use scaler_state;

    // set new historics
    var historics = historics_state.get();
    historics.fromString(new_historics);

    // normalise the historics
    var scaler = scaler_state.get();
    var scaled_historics = scaler.normalise(historics);
    
    // make prediction with normalised historics
    var g = graph_state.get();
    g.setInput("Input", scaled_historics);
    var prediction = g.evaluate("Output");
    var squeezed_pred = prediction.squeeze();
    
    // descale the predictions
    var descaled_pred = scaler.deNormalise(squeezed_pred);

    // set new historics and graph states
    historics_state.set(historics);
    graph_state.set(g);
    prediction_state.set(descaled_pred);
endfunction

// method for querying currently set historics
@query
function getHistorics() : String
    use historics_state;
    var historics = historics_state.get();
    var squeezed_historics = historics.squeeze();
    return squeezed_historics.toString();
endfunction

// Method to make a single prediction based on currently set historics
@query
function makePrediction() : String
    use prediction_state;
    var pred = prediction_state.get();
    return pred.toString();
endfunction

// Method for overwriting the current graph
// this can be used either to update the weights
// or to replace with a totally new model
@action
function updateGraph(graph_string : String)
    use graph_state;
    var g = graph_state.get();
    g = g.deserializeFromString(graph_string);
    graph_state.set(g);
endfunction

// method to train the existing graph with current historics data
// labels must be provided
@action
function train(train_labels_string: String)
    use historics_state;
    use graph_state;
    use dataloader_state;
    use optimiser_state;
    
    // retrieve the latest graph
    var g = graph_state.get();
    
    // retrieve the historics
    var historics = historics_state.get();
 
    // retrieve dataloader
    var dataloader = dataloader_state.get();
    
    // add the historics as training data, and add provided labels
    var tensor_shape = Array<UInt64>(1);
    tensor_shape[0] = 1u64;
    var train_labels = Tensor(tensor_shape);
    train_labels.fromString(train_labels_string);
    dataloader.addData(historics, train_labels);
     
    // retrieve the optimiser
    var optimiser = optimiser_state.get();
    optimiser.setGraph(g);
    optimiser.setDataloader(dataloader);
 
    var training_iterations = 1;
    var batch_size = 8u64;
    for(i in 0:training_iterations)
        var loss = optimiser.run(batch_size);
    endfor
endfunction
"""

def main():

    # create our first private key pair
    entity1 = Entity()

    # build the ledger API
    api = LedgerApi('127.0.0.1', 8100)

    # create wealth so that we have the funds to be able to create contracts on the network
    api.sync(api.tokens.wealth(entity1, 1000000000000000))

    # create the smart contract
    contract = SmartContract(CONTRACT_TEXT)

    # deploy the contract to the network
    api.sync(api.contracts.create(entity1, contract, 1000000000))

    # update the graph with a new model
    fet_tx_fee = 100000000
    with open(GRAPH_FILE_NAME, mode='rb') as file:
        print("reading in graph file...")
        rfile = file.read()

        print("encoding to base64 string...")
        b64obj = base64.b64encode(rfile)
        obj = b64obj.decode()

        print("updating smart contract graph...")
        api.sync(contract.action(api, 'updateGraph', fet_tx_fee, [entity1], obj))

    print("finished updating smart contract graph")

    fet_tx_fee = 100000000

    # set the scale of values to normalise to
    api.sync(contract.action(api, 'setScale', fet_tx_fee, [entity1], 0, 15000))

    # set one real example input data set
    api.sync(contract.action(api, 'setHistorics', fet_tx_fee, [entity1], EXAMPLE_INPUT_HISTORICS))

    current_historics = contract.query(api, 'getHistorics')
    print("current historics: " + current_historics)

    # make a prediction
    current_prediction = contract.query(api, 'makePrediction')
    print("current prediction: " + current_prediction)

    # check training
    # api.sync(contract.action(api, 'train', fet_tx_fee, [entity1], EXAMPLE_LABEL_HISTORICS))

if __name__ == '__main__':
    main()
