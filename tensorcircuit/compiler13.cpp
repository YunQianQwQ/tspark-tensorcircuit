#include <pybind11/pybind11.h>
#include <string>

#include<iostream>
#include<sstream>
#include<algorithm>
#include<map>
#include<queue>
#include<random>
#include<string>
#include<vector>
#define F(i,l,r) for(int i=(l),i##_end=(r);i<i##_end;++i)
using namespace std;
constexpr int diameter=4;
mt19937 rnd(0);
struct physical_gate
{
	int u,v;
	double w;
};
int n_qubit;
vector<double> F1;
vector<physical_gate> F2;
map<pair<int,int>,double> F2M;
void init()
{
	F1={96,89,95,84,92,95,96,94,93,94,94,94,93};
	for(double &i:F1)i=(100-i)/1e4;
	F2={
		{ 5, 6,897},
		{ 4, 6,851},
		{ 6, 7,854},
		{ 4, 1,901},
		{ 6, 3,938},
		{ 2, 1,896},
		{ 1, 3,823},
		{ 3, 8,944},
		{ 8, 9,978},
		{ 1, 0,945},
		{ 3,12,940},
		{ 8,10,929},
		{ 0,12,946},
		{12,10,910},
		{12,11,950},
	};
	for(physical_gate &i:F2)i.w=(1000-i.w)/1e4;
	n_qubit=(int)F1.size();
// minimize number of gates
	for(double &i:F1)i+=1e3;
	for(physical_gate &i:F2)i.w+=1e3;
	for(physical_gate &i:F2)
	{
		F2M[pair<int,int>(i.v,i.u)]=i.w;
		F2M[pair<int,int>(i.u,i.v)]=i.w;
	}
}
struct gate
{
	string name;
	vector<int> operand;
};
int n_gate;
vector<gate> a;
vector<vector<int>> en,ep;
stringstream iss;
stringstream oss;
bool read_gate()
{
	string command,name;
	vector<int> operand;
	getline(iss,command);
	int i=(int)command.find(" q[");
	if(i==(int)string::npos)return false;
	name=command.substr(0,i);
	while((i=(int)command.find("q[",i))!=(int)string::npos)
	{
		i+=2;
		size_t len;
		operand.emplace_back(stoi(command.substr(i),&len));
		i+=(int)len;
	}
	if(name!="QREG")a.push_back({name,operand});
	return true;
}
void calc_dependence()
{
	en.resize(n_gate);
	ep.resize(n_gate);
	vector<int> la(n_qubit,-1);
	F(i,0,n_gate)
	{
		for(int j:a[i].operand)
		{
			if(~la[j])
			{
				en[la[j]].emplace_back(i);
				ep[i].emplace_back(la[j]);
			}
			la[j]=i;
		}
	}
}
vector<int> prio;
struct node_prio
{
	int u;
	friend bool operator<(const node_prio &x,const node_prio &y){return prio[x.u]<prio[y.u];}
};
vector<int> gen_order()
{
	prio=vector<int>(n_gate);
	vector<int> deg(n_gate);
	F(i,0,n_gate)prio[i]=i,deg[i]=(int)ep[i].size();
	shuffle(prio.begin(),prio.end(),rnd);
	priority_queue<node_prio> pq;
	F(i,0,n_gate)if(!deg[i])pq.push({i});
	vector<int> order;
	while(!pq.empty())
	{
		int u=pq.top().u;pq.pop();
		order.emplace_back(u);
		for(int v:en[u])if(!--deg[v])pq.push({v});
	}
	return order;
}
struct state
{
	vector<int> st,po;
	vector<gate> ga;
	double loss,est;
	gate embed(gate u)
	{
		for(int &i:u.operand)i=po[i];
		return u;
	}
	void append(const gate &u)
	{
		ga.emplace_back(u);
		if(u.operand.size()==1)loss+=F1[u.operand[0]];
		else if(u.operand.size()==2)loss+=F2M[pair<int,int>(u.operand[0],u.operand[1])];
		else throw;
	}
	void perform_swap(int u,int v)
	{
		if(!~st[u]&&!~st[v]);
		else if(!~st[u])
		{
			append({"CX",{v,u}});
			append({"CX",{u,v}});
		}
		else if(!~st[v])
		{
			append({"CX",{u,v}});
			append({"CX",{v,u}});
		}
		else
		{
			append({"CX",{u,v}});
			append({"CX",{v,u}});
			append({"CX",{u,v}});
		}
		swap(st[u],st[v]);
		if(~st[u])po[st[u]]=u;
		if(~st[v])po[st[v]]=v;
	}
};
double calc_dist(int i,const state &st)
{
	if(a[i].operand.size()!=2)return 0;
	int u=a[i].operand[0],v=a[i].operand[1];
	u=st.po[u];v=st.po[v];
	if(!~(u&v))return 0;
	auto single_source=[&](int s)->vector<double>
	{
		vector<double> dis(n_qubit,1e18);
		if(~s)dis[s]=0;
		else F(j,0,n_qubit)if(!~st.st[j])dis[j]=0;
		F(ii,0,diameter)for(const physical_gate &g:F2)
		{
			dis[g.u]=min(dis[g.u],dis[g.v]+(3-!~s-!~st.st[g.u])*g.w);
			dis[g.v]=min(dis[g.v],dis[g.u]+(3-!~s-!~st.st[g.v])*g.w);
		}
		return dis;
	};
	vector<double> dis_u=single_source(u);
	vector<double> dis_v=single_source(v);
	double ans=1e18;
	for(const physical_gate &g:F2)
	{
		ans=min(ans,dis_u[g.u]+dis_v[g.v]);
		ans=min(ans,dis_u[g.v]+dis_v[g.u]);
	}
	return ans;
}
vector<int> lapa;
void perform(vector<state> &vs,int i,state st,int avoid=-1)
{
	if(a[i].operand.size()!=2)throw;
	int u=a[i].operand[0],v=a[i].operand[1];
	u=st.po[u];v=st.po[v];
	if(!~(u|v))throw;
	auto single_source=[&](int s)->vector<pair<double,int>>
	{
		vector<pair<double,int>> dis(n_qubit,{1e18,-1});
		dis[s]={0,-1};
		F(ii,0,diameter)for(const physical_gate &g:F2)if(g.u!=avoid&&g.v!=avoid)
		{
			dis[g.u]=min(dis[g.u],{dis[g.v].first+(3-!~st.st[g.u])*g.w,g.v});
			dis[g.v]=min(dis[g.v],{dis[g.u].first+(3-!~st.st[g.v])*g.w,g.u});
		}
		return dis;
	};
	vector<pair<double,int>> dis_u=single_source(u);
	vector<pair<double,int>> dis_v=single_source(v);
	pair<double,pair<int,int>> ans={1e18,{-1,-1}};
	for(const physical_gate &g:F2)
	{
		ans=min(ans,{dis_u[g.u].first+dis_v[g.v].first,{g.u,g.v}});
		ans=min(ans,{dis_u[g.v].first+dis_v[g.u].first,{g.v,g.u}});
	}
	if(!~ans.second.first)return;
	vector<int> upa,vpa;lapa.clear();
	for(int z=ans.second.first;z!=u;z=dis_u[z].second)upa.emplace_back(z),lapa.emplace_back(z);
	upa.emplace_back(u);
	for(int z=ans.second.second;z!=v;z=dis_v[z].second)vpa.emplace_back(z),lapa.emplace_back(z);
	vpa.emplace_back(v);
	for(int j=(int)upa.size()-1;~--j;)st.perform_swap(upa[j],upa[j+1]);
	for(int j=(int)vpa.size()-1;~--j;)st.perform_swap(vpa[j],vpa[j+1]);
	st.append(st.embed(a[i]));
	vs.emplace_back(st);
}
double estimate(int l,const state &st)
{
	double sum=0,coef=1;
	F(i,l,n_gate)
	{
		if(coef<0.1)break;
		sum+=calc_dist(i,st)*coef;
		coef*=a[i].operand.size()>1?0.5:1;
	}
	return sum;
}
vector<state> choose(int l,vector<state> &g)
{
	vector<state> f,h;
	sort(g.begin(),g.end(),[](const state &u,const state &v){return u.st!=v.st?u.st<v.st:u.loss<v.loss;});
	F(i,0,(int)g.size())if(!i||g[i].st!=g[i-1].st)h.emplace_back(move(g[i]));
	g=move(h);
	for(state &s:g)s.est=estimate(l,s);
	F(i,0,5)
	{
		double coef=0.04+0.24*i;
		sort(g.begin(),g.end(),[&](const state &u,const state &v){return u.loss+coef*u.est>v.loss+coef*v.est;});
		int m=(int)g.size();
		F(j,max(m-100,0),m)f.emplace_back(move(g[j]));
		g.resize(max(m-100,0));
	}
	return f;
}
vector<state> f;
void add_qubit(int l,int u)
{
	vector<state> g;
	for(const state &s:f)F(i,0,n_qubit)if(!~s.st[i])
	{
		state t=s;
		t.po[u]=i;
		t.st[i]=u;
		g.emplace_back(t);
	}
	f=choose(l,g);
}
pair<double,state> ans;
void plan()
{
	f={{vector<int>(n_qubit,-1),vector<int>(n_qubit,-1),{},0,0}};
	vector<bool> occ(n_qubit);
	F(i,0,n_gate)
	{
		for(int j:a[i].operand)if(!occ[j])add_qubit(i,j),occ[j]=true;
		if(a[i].operand.size()==1)
		{
			for(state &s:f)s.append(s.embed(a[i]));
			continue;
		}
		if(a[i].operand.size()!=2)throw;
		vector<state> g;
		for(const state &s:f)
		{
			perform(g,i,s);
			vector<int> z=lapa;
			for(int j:z)perform(g,i,s,j);
		}
		f=choose(i+1,g);
	}
	for(const state &s:f)ans=min(ans,{s.loss,s},[](const pair<double,state> &u,const pair<double,state> &v){return u.first<v.first;});
}
void process1()
{
	init();
	while(read_gate());
	n_gate=(int)a.size();
	calc_dependence();
	ans.first=1e18;
	F(i,0,50)
	{
		vector<int> order=gen_order();
		vector<gate> pa;
		F(j,0,n_gate)pa.emplace_back(a[order[j]]);
		swap(a,pa);
		plan();
		swap(a,pa);
	}
//	cerr<<ans.first<<endl;
	oss<<"QREG q["<<n_qubit<<"];\n";
	for(const gate &g:ans.second.ga)
	{
		oss<<g.name;
		F(i,0,(int)g.operand.size())
		{
			oss<<(i?", ":" ")<<"q["<<g.operand[i]<<"]";
		}
		oss<<";\n";
	}
	vector<bool> occ(n_qubit);
	for(int &i:ans.second.po)if(~i)occ[i]=true;
	oss<<"//";
	for(int &i:ans.second.po)
	{
		if(!~i)
		{
			i=0;
			while(occ[i])++i;
			occ[i]=true;
		}
		oss<<" "<<i;
	}
	oss<<"\n";
}

static std::string process(const std::string& s) {
    int pos1=(int)s.rfind("}");
    if(pos1==(int)s.size())pos1=0;else ++pos1;
    int pos2=(int)s.find("TQASM");
    if(pos2!=(int)string::npos)pos2=(int)s.find(";",pos2)+1;
    int prefix_len=min(max(pos1,pos2),(int)s.size());
    if(s[prefix_len]=='\n')++prefix_len;
    iss.str(s.substr(prefix_len));
    process1();
    return s.substr(0,prefix_len)+oss.str();
}

namespace py = pybind11;

PYBIND11_MODULE(quantum_compiler, m) {
    m.doc() = "quantum compiler";
    m.def("process", &process, py::arg("s"));
}
