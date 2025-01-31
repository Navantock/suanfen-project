import torch

from torch_geometric.datasets import Planetoid, WebKB, WikipediaNetwork

import pdb
from utils import set_seed_global
from configs import args
from train import train_model
from models.acm import ACM_Framework, HighOrder_ACM_Framework, ACM_GNN
from models.layers import ACM_GCN_Filter, ACM_GAT_Filter, HighOrder_ACM_GCN_Filter

if __name__ == '__main__':
    print(args)
    set_seed_global(args.seed)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # Fetch datasets, data, and masks
    if args.dataset in ['cora']:
        dataset = Planetoid(root='./datasets',
                            name=args.dataset,
                            transform=None)
    elif args.dataset in ['texas']:
        dataset = WebKB(root='./datasets', name=args.dataset, transform=None)
    elif args.dataset in ['chameleon']:
        dataset = WikipediaNetwork(root='./datasets',
                                   name=args.dataset,
                                   transform=None)
    else:
        raise NotImplementedError

    data = dataset[0].to(device)

    # Create model
    # model for Texas
    model = ACM_GNN(in_dim=data.num_node_features,
                    out_dim=dataset.num_classes,
                    hidden_dim=args.hidden_dim,
                    ACM_Framework=HighOrder_ACM_Framework,
                    ACM_Filter=HighOrder_ACM_GCN_Filter,
                    mix=True,
                    improve=False,
                    dropout=args.dp).to(device)
    """model = ACM_GNN(in_dim=data.num_node_features,
                    out_dim=dataset.num_classes,
                    hidden_dim=args.hidden_dim,
                    ACM_Framework=ACM_Framework,
                    ACM_Filter=ACM_GCN_Filter,
                    mix=True,
                    improve=False,
                    dropout=args.dp).to(device)"""
    # Train model
    if args.dataset in ["texas", "chameleon"]:
        val_test_acc = []
        for i in range(10):
            print("{}: Training on mask {}.".format(args.dataset.capitalize(), i + 1))
            train_mask = data.train_mask[:, i]
            val_mask = data.val_mask[:, i]
            test_mask = data.test_mask[:, i]
            val_test_acc.append(train_model(model, data, train_mask, val_mask, test_mask))
        print("{}: Average test_acc {:.3}".format(args.dataset.capitalize(), sum(val_test_acc) / 10))
    else:
        train_model(model, data, data.train_mask, data.val_mask, data.test_mask)
