var refreshIntervalId = 0;
var refreshTime = 60000;

$(function(){
	
	//var element =  document.getElementById("eps_db_autorefresh");
	/*if (typeof(element) != 'undefined' && element != null)
	{
		if(document.getElementById("eps_db_autorefresh").value == "On"){
			refreshIntervalId = setInterval(function(){ 
				showDashboard(getActiveWorkspace(), false, 'default', 'EPS_DATA_REQ', 0, 0, null, null);
				var dataapi={};
				dataapi['transName']=getActiveWorkspace();
				loadAgentInfo(dataapi,$('#idevice_summary'));
			}, 
			refreshTime);
		}
		else
		{
			clearInterval(refreshIntervalId);
		}
	}*/
});

var dashboard_context = {
	no_of_events:10,
	is_autorefresh_enabled:0,
	autorefresh_dashboard:null,
	autorefresh_interval:15,
	evrate_timeout_retvalue:null,
	db_timeout_retvalue:null,
	metric_timeout_retvalue:null,
	current_context:null,
	metadata_list:{},
	selected_metric_list:[],
	metric_db_handle:null, 
	graph1:null,
	graph2:null,
	pie1:null,
	alertHandle:null,
	scriptDashboardTableObj:null,
	dbTableObj:null,
	metricTableObj:null,
};

// random_colors_list length:133
var random_colors_list = [
    {
        "hex": "#f56954", 
        "name": "Mat Red", 
        "rgb": "(245,105,84)"
    },
	{
        "hex": "#00a65a", 
        "name": "Mat Green", 
        "rgb": "(0,166,90)"
    },
	{
        "hex": "#f39c12", 
        "name": "Mat Orange", 
        "rgb": "(243,156,18)"
    },
	{
        "hex": "#00c0ef", 
        "name": "Mat Blue", 
        "rgb": "(0,192,239)"
    },
	{
        "hex": "#3c8dbc", 
        "name": "Mat Sky Blue", 
        "rgb": "(60,141,188)"
    },
	{
        "hex": "#d2d6de", 
        "name": "Mat Grey", 
        "rgb": "(210,214,222)"
    },
    {
        "hex": "#EFDECD", 
        "name": "Almond", 
        "rgb": "(239, 222, 205)"
    }, 
    {
        "hex": "#CD9575", 
        "name": "Antique Brass", 
        "rgb": "(205, 149, 117)"
    }, 
    {
        "hex": "#FDD9B5", 
        "name": "Apricot", 
        "rgb": "(253, 217, 181)"
    }, 
    {
        "hex": "#78DBE2", 
        "name": "Aquamarine", 
        "rgb": "(120, 219, 226)"
    }, 
    {
        "hex": "#87A96B", 
        "name": "Asparagus", 
        "rgb": "(135, 169, 107)"
    }, 
    {
        "hex": "#FFA474", 
        "name": "Atomic Tangerine", 
        "rgb": "(255, 164, 116)"
    }, 
    {
        "hex": "#FAE7B5", 
        "name": "Banana Mania", 
        "rgb": "(250, 231, 181)"
    }, 
    {
        "hex": "#9F8170", 
        "name": "Beaver", 
        "rgb": "(159, 129, 112)"
    }, 
    {
        "hex": "#FD7C6E", 
        "name": "Bittersweet", 
        "rgb": "(253, 124, 110)"
    }, 
    {
        "hex": "#000000", 
        "name": "Black", 
        "rgb": "(0,0,0)"
    }, 
    {
        "hex": "#ACE5EE", 
        "name": "Blizzard Blue", 
        "rgb": "(172, 229, 238)"
    }, 
    {
        "hex": "#1F75FE", 
        "name": "Blue", 
        "rgb": "(31, 117, 254)"
    }, 
    {
        "hex": "#A2A2D0", 
        "name": "Blue Bell", 
        "rgb": "(162, 162, 208)"
    }, 
    {
        "hex": "#6699CC", 
        "name": "Blue Gray", 
        "rgb": "(102, 153, 204)"
    }, 
    {
        "hex": "#0D98BA", 
        "name": "Blue Green", 
        "rgb": "(13, 152, 186)"
    }, 
    {
        "hex": "#7366BD", 
        "name": "Blue Violet", 
        "rgb": "(115, 102, 189)"
    }, 
    {
        "hex": "#DE5D83", 
        "name": "Blush", 
        "rgb": "(222, 93, 131)"
    }, 
    {
        "hex": "#CB4154", 
        "name": "Brick Red", 
        "rgb": "(203, 65, 84)"
    }, 
    {
        "hex": "#B4674D", 
        "name": "Brown", 
        "rgb": "(180, 103, 77)"
    }, 
    {
        "hex": "#FF7F49", 
        "name": "Burnt Orange", 
        "rgb": "(255, 127, 73)"
    }, 
    {
        "hex": "#EA7E5D", 
        "name": "Burnt Sienna", 
        "rgb": "(234, 126, 93)"
    }, 
    {
        "hex": "#B0B7C6", 
        "name": "Cadet Blue", 
        "rgb": "(176, 183, 198)"
    }, 
    {
        "hex": "#FFFF99", 
        "name": "Canary", 
        "rgb": "(255, 255, 153)"
    }, 
    {
        "hex": "#1CD3A2", 
        "name": "Caribbean Green", 
        "rgb": "(28, 211, 162)"
    }, 
    {
        "hex": "#FFAACC", 
        "name": "Carnation Pink", 
        "rgb": "(255, 170, 204)"
    }, 
    {
        "hex": "#DD4492", 
        "name": "Cerise", 
        "rgb": "(221, 68, 146)"
    }, 
    {
        "hex": "#1DACD6", 
        "name": "Cerulean", 
        "rgb": "(29, 172, 214)"
    }, 
    {
        "hex": "#BC5D58", 
        "name": "Chestnut", 
        "rgb": "(188, 93, 88)"
    }, 
    {
        "hex": "#DD9475", 
        "name": "Copper", 
        "rgb": "(221, 148, 117)"
    }, 
    {
        "hex": "#9ACEEB", 
        "name": "Cornflower", 
        "rgb": "(154, 206, 235)"
    }, 
    {
        "hex": "#FFBCD9", 
        "name": "Cotton Candy", 
        "rgb": "(255, 188, 217)"
    }, 
    {
        "hex": "#FDDB6D", 
        "name": "Dandelion", 
        "rgb": "(253, 219, 109)"
    }, 
    {
        "hex": "#2B6CC4", 
        "name": "Denim", 
        "rgb": "(43, 108, 196)"
    }, 
    {
        "hex": "#EFCDB8", 
        "name": "Desert Sand", 
        "rgb": "(239, 205, 184)"
    }, 
    {
        "hex": "#6E5160", 
        "name": "Eggplant", 
        "rgb": "(110, 81, 96)"
    }, 
    {
        "hex": "#CEFF1D", 
        "name": "Electric Lime", 
        "rgb": "(206, 255, 29)"
    }, 
    {
        "hex": "#71BC78", 
        "name": "Fern", 
        "rgb": "(113, 188, 120)"
    }, 
    {
        "hex": "#6DAE81", 
        "name": "Forest Green", 
        "rgb": "(109, 174, 129)"
    }, 
    {
        "hex": "#C364C5", 
        "name": "Fuchsia", 
        "rgb": "(195, 100, 197)"
    }, 
    {
        "hex": "#CC6666", 
        "name": "Fuzzy Wuzzy", 
        "rgb": "(204, 102, 102)"
    }, 
    {
        "hex": "#E7C697", 
        "name": "Gold", 
        "rgb": "(231, 198, 151)"
    }, 
    {
        "hex": "#FCD975", 
        "name": "Goldenrod", 
        "rgb": "(252, 217, 117)"
    }, 
    {
        "hex": "#A8E4A0", 
        "name": "Granny Smith Apple", 
        "rgb": "(168, 228, 160)"
    }, 
    {
        "hex": "#95918C", 
        "name": "Gray", 
        "rgb": "(149, 145, 140)"
    }, 
    {
        "hex": "#1CAC78", 
        "name": "Green", 
        "rgb": "(28, 172, 120)"
    }, 
    {
        "hex": "#1164B4", 
        "name": "Green Blue", 
        "rgb": "(17, 100, 180)"
    }, 
    {
        "hex": "#F0E891", 
        "name": "Green Yellow", 
        "rgb": "(240, 232, 145)"
    }, 
    {
        "hex": "#FF1DCE", 
        "name": "Hot Magenta", 
        "rgb": "(255, 29, 206)"
    }, 
    {
        "hex": "#B2EC5D", 
        "name": "Inchworm", 
        "rgb": "(178, 236, 93)"
    }, 
    {
        "hex": "#5D76CB", 
        "name": "Indigo", 
        "rgb": "(93, 118, 203)"
    }, 
    {
        "hex": "#CA3767", 
        "name": "Jazzberry Jam", 
        "rgb": "(202, 55, 103)"
    }, 
    {
        "hex": "#3BB08F", 
        "name": "Jungle Green", 
        "rgb": "(59, 176, 143)"
    }, 
    {
        "hex": "#FEFE22", 
        "name": "Laser Lemon", 
        "rgb": "(254, 254, 34)"
    }, 
    {
        "hex": "#FCB4D5", 
        "name": "Lavender", 
        "rgb": "(252, 180, 213)"
    }, 
    {
        "hex": "#FFF44F", 
        "name": "Lemon Yellow", 
        "rgb": "(255, 244, 79)"
    }, 
    {
        "hex": "#FFBD88", 
        "name": "Macaroni and Cheese", 
        "rgb": "(255, 189, 136)"
    }, 
    {
        "hex": "#F664AF", 
        "name": "Magenta", 
        "rgb": "(246, 100, 175)"
    }, 
    {
        "hex": "#AAF0D1", 
        "name": "Magic Mint", 
        "rgb": "(170, 240, 209)"
    }, 
    {
        "hex": "#CD4A4C", 
        "name": "Mahogany", 
        "rgb": "(205, 74, 76)"
    }, 
    {
        "hex": "#EDD19C", 
        "name": "Maize", 
        "rgb": "(237, 209, 156)"
    }, 
    {
        "hex": "#979AAA", 
        "name": "Manatee", 
        "rgb": "(151, 154, 170)"
    }, 
    {
        "hex": "#FF8243", 
        "name": "Mango Tango", 
        "rgb": "(255, 130, 67)"
    }, 
    {
        "hex": "#C8385A", 
        "name": "Maroon", 
        "rgb": "(200, 56, 90)"
    }, 
    {
        "hex": "#EF98AA", 
        "name": "Mauvelous", 
        "rgb": "(239, 152, 170)"
    }, 
    {
        "hex": "#FDBCB4", 
        "name": "Melon", 
        "rgb": "(253, 188, 180)"
    }, 
    {
        "hex": "#1A4876", 
        "name": "Midnight Blue", 
        "rgb": "(26, 72, 118)"
    }, 
    {
        "hex": "#30BA8F", 
        "name": "Mountain Meadow", 
        "rgb": "(48, 186, 143)"
    }, 
    {
        "hex": "#C54B8C", 
        "name": "Mulberry", 
        "rgb": "(197, 75, 140)"
    }, 
    {
        "hex": "#1974D2", 
        "name": "Navy Blue", 
        "rgb": "(25, 116, 210)"
    }, 
    {
        "hex": "#FFA343", 
        "name": "Neon Carrot", 
        "rgb": "(255, 163, 67)"
    }, 
    {
        "hex": "#BAB86C", 
        "name": "Olive Green", 
        "rgb": "(186, 184, 108)"
    }, 
    {
        "hex": "#FF7538", 
        "name": "Orange", 
        "rgb": "(255, 117, 56)"
    }, 
    {
        "hex": "#FF2B2B", 
        "name": "Orange Red", 
        "rgb": "(255, 43, 43)"
    }, 
    {
        "hex": "#F8D568", 
        "name": "Orange Yellow", 
        "rgb": "(248, 213, 104)"
    }, 
    {
        "hex": "#E6A8D7", 
        "name": "Orchid", 
        "rgb": "(230, 168, 215)"
    }, 
    {
        "hex": "#414A4C", 
        "name": "Outer Space", 
        "rgb": "(65, 74, 76)"
    }, 
    {
        "hex": "#FF6E4A", 
        "name": "Outrageous Orange", 
        "rgb": "(255, 110, 74)"
    }, 
    {
        "hex": "#1CA9C9", 
        "name": "Pacific Blue", 
        "rgb": "(28, 169, 201)"
    }, 
    {
        "hex": "#FFCFAB", 
        "name": "Peach", 
        "rgb": "(255, 207, 171)"
    }, 
    {
        "hex": "#C5D0E6", 
        "name": "Periwinkle", 
        "rgb": "(197, 208, 230)"
    }, 
    {
        "hex": "#FDDDE6", 
        "name": "Piggy Pink", 
        "rgb": "(253, 221, 230)"
    }, 
    {
        "hex": "#158078", 
        "name": "Pine Green", 
        "rgb": "(21, 128, 120)"
    }, 
    {
        "hex": "#FC74FD", 
        "name": "Pink Flamingo", 
        "rgb": "(252, 116, 253)"
    }, 
    {
        "hex": "#F78FA7", 
        "name": "Pink Sherbet", 
        "rgb": "(247, 143, 167)"
    }, 
    {
        "hex": "#8E4585", 
        "name": "Plum", 
        "rgb": "(142, 69, 133)"
    }, 
    {
        "hex": "#7442C8", 
        "name": "Purple Heart", 
        "rgb": "(116, 66, 200)"
    }, 
    {
        "hex": "#9D81BA", 
        "name": "Purple Mountain's Majesty", 
        "rgb": "(157, 129, 186)"
    }, 
    {
        "hex": "#FE4EDA", 
        "name": "Purple Pizzazz", 
        "rgb": "(254, 78, 218)"
    }, 
    {
        "hex": "#FF496C", 
        "name": "Radical Red", 
        "rgb": "(255, 73, 108)"
    }, 
    {
        "hex": "#D68A59", 
        "name": "Raw Sienna", 
        "rgb": "(214, 138, 89)"
    }, 
    {
        "hex": "#714B23", 
        "name": "Raw Umber", 
        "rgb": "(113, 75, 35)"
    }, 
    {
        "hex": "#FF48D0", 
        "name": "Razzle Dazzle Rose", 
        "rgb": "(255, 72, 208)"
    }, 
    {
        "hex": "#E3256B", 
        "name": "Razzmatazz", 
        "rgb": "(227, 37, 107)"
    }, 
    {
        "hex": "#EE204D", 
        "name": "Red", 
        "rgb": "(238,32 ,77 )"
    }, 
    {
        "hex": "#FF5349", 
        "name": "Red Orange", 
        "rgb": "(255, 83, 73)"
    }, 
    {
        "hex": "#C0448F", 
        "name": "Red Violet", 
        "rgb": "(192, 68, 143)"
    }, 
    {
        "hex": "#1FCECB", 
        "name": "Robin's Egg Blue", 
        "rgb": "(31, 206, 203)"
    }, 
    {
        "hex": "#7851A9", 
        "name": "Royal Purple", 
        "rgb": "(120, 81, 169)"
    }, 
    {
        "hex": "#FF9BAA", 
        "name": "Salmon", 
        "rgb": "(255, 155, 170)"
    }, 
    {
        "hex": "#FC2847", 
        "name": "Scarlet", 
        "rgb": "(252, 40, 71)"
    }, 
    {
        "hex": "#76FF7A", 
        "name": "Screamin' Green", 
        "rgb": "(118, 255, 122)"
    }, 
    {
        "hex": "#9FE2BF", 
        "name": "Sea Green", 
        "rgb": "(159, 226, 191)"
    }, 
    {
        "hex": "#A5694F", 
        "name": "Sepia", 
        "rgb": "(165, 105, 79)"
    }, 
    {
        "hex": "#8A795D", 
        "name": "Shadow", 
        "rgb": "(138, 121, 93)"
    }, 
    {
        "hex": "#45CEA2", 
        "name": "Shamrock", 
        "rgb": "(69, 206, 162)"
    }, 
    {
        "hex": "#FB7EFD", 
        "name": "Shocking Pink", 
        "rgb": "(251, 126, 253)"
    }, 
    {
        "hex": "#CDC5C2", 
        "name": "Silver", 
        "rgb": "(205, 197, 194)"
    }, 
    {
        "hex": "#80DAEB", 
        "name": "Sky Blue", 
        "rgb": "(128, 218, 235)"
    }, 
    {
        "hex": "#ECEABE", 
        "name": "Spring Green", 
        "rgb": "(236, 234, 190)"
    }, 
    {
        "hex": "#FFCF48", 
        "name": "Sunglow", 
        "rgb": "(255, 207, 72)"
    }, 
    {
        "hex": "#FD5E53", 
        "name": "Sunset Orange", 
        "rgb": "(253, 94, 83)"
    }, 
    {
        "hex": "#FAA76C", 
        "name": "Tan", 
        "rgb": "(250, 167, 108)"
    }, 
    {
        "hex": "#18A7B5", 
        "name": "Teal Blue", 
        "rgb": "(24, 167, 181)"
    }, 
    {
        "hex": "#EBC7DF", 
        "name": "Thistle", 
        "rgb": "(235, 199, 223)"
    }, 
    {
        "hex": "#FC89AC", 
        "name": "Tickle Me Pink", 
        "rgb": "(252, 137, 172)"
    }, 
    {
        "hex": "#DBD7D2", 
        "name": "Timberwolf", 
        "rgb": "(219, 215, 210)"
    }, 
    {
        "hex": "#17806D", 
        "name": "Tropical Rain Forest", 
        "rgb": "(23, 128, 109)"
    }, 
    {
        "hex": "#DEAA88", 
        "name": "Tumbleweed", 
        "rgb": "(222, 170, 136)"
    }, 
    {
        "hex": "#77DDE7", 
        "name": "Turquoise Blue", 
        "rgb": "(119, 221, 231)"
    }, 
    {
        "hex": "#FFFF66", 
        "name": "Unmellow Yellow", 
        "rgb": "(255, 255, 102)"
    }, 
    {
        "hex": "#926EAE", 
        "name": "Violet (Purple)", 
        "rgb": "(146, 110, 174)"
    }, 
    {
        "hex": "#324AB2", 
        "name": "Violet Blue", 
        "rgb": "(50, 74, 178)"
    }, 
    {
        "hex": "#F75394", 
        "name": "Violet Red", 
        "rgb": "(247, 83, 148)"
    }, 
    {
        "hex": "#FFA089", 
        "name": "Vivid Tangerine", 
        "rgb": "(255, 160, 137)"
    }, 
    {
        "hex": "#8F509D", 
        "name": "Vivid Violet", 
        "rgb": "(143, 80, 157)"
    }, 
    {
        "hex": "#FFFFFF", 
        "name": "White", 
        "rgb": "(255, 255, 255)"
    }, 
    {
        "hex": "#A2ADD0", 
        "name": "Wild Blue Yonder", 
        "rgb": "(162, 173, 208)"
    }, 
    {
        "hex": "#FF43A4", 
        "name": "Wild Strawberry", 
        "rgb": "(255, 67, 164)"
    }, 
    {
        "hex": "#FC6C85", 
        "name": "Wild Watermelon", 
        "rgb": "(252, 108, 133)"
    }, 
    {
        "hex": "#CDA4DE", 
        "name": "Wisteria", 
        "rgb": "(205, 164, 222)"
    }, 
    {
        "hex": "#FCE883", 
        "name": "Yellow", 
        "rgb": "(252, 232, 131)"
    }, 
    {
        "hex": "#C5E384", 
        "name": "Yellow Green", 
        "rgb": "(197, 227, 132)"
    }, 
    {
        "hex": "#FFAE42", 
        "name": "Yellow Orange", 
        "rgb": "(255, 174, 66)"
    }
]

var rgb_color_list = [[142,142,56],[113,198,113],[76,76,76],[102,102,102],[127,127,127],[153,153,153],[178,178,178],[204,204,204],[229,229,229],[205,0,205],[69,139,116],[197,193,170],[209,108,35],[209,255,35],[0,255,0],[21,206,210],[21,111,210],[0,0,255],[131,21,210],[255,0,255],[230,178,191],[255,178,178],[241,210,189],[241,255,189],[178,255,178],[184,240,241],[184,211,241],[178,178,255],[217,184,241],[255,178,255],[213,127,149],[255,127,127],[232,181,145],[232,255,145],[127,255,127],[138,230,232],[138,183,232],[127,127,255],[193,138,232],[255,127,255],[192,63,96],[255,63,63],[220,144,90],[220,255,90],[63,255,63],[79,218,221],[79,147,221],[63,63,255],[162,79,221],[255,63,255],[142,56,142],[0,205,205],[167,86,28],[167,204,28],[0,204,0],[16,164,168],[16,88,168],[0,0,204],[104,16,168],[204,0,204],[113,113,198],[56,142,142],[125,64,21],[125,153,21],[0,153,0],[12,123,126],[12,66,126],[0,0,153],[78,12,126],[153,0,153],[68,0,17],[125,158,192],[83,43,14],[83,102,14],[0,102,0],[8,82,84],[8,44,84],[0,0,102],[52,8,84],[102,0,102]];



function randomColorFactor() {
			return Math.round(Math.random() * 255);
		}

function randomColor(opacity) {
			return 'rgba(' + randomColorFactor() + ',' + randomColorFactor() + ',' + randomColorFactor() + ',' + (opacity || '.3') + ')';
		}

function getRGBColor(number,opacity)
{
	//var rgb_array = ((random_colors_list[number]['rgb']).replace(/[{()}]/g, '')).split(',');
	var rgb_array = rgb_color_list[number];
	return 'rgba(' + rgb_array[0] + ',' + rgb_array[1] + ',' + rgb_array[2] + ',' + (opacity || '.3') + ')';
}

function getHexColor(number)
{
	var rgb_array = random_colors_list[number]['hex'];
	return rgb_array;
}


