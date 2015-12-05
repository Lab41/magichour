package logtree;

public enum LogElemLabel {
	INT {
		@Override
		public String toString() {
			return "INT";
		}
	},
	ID {
		@Override
		public String toString() {
			return "ID";
		}
	},
	STR{
		@Override
		public String toString() {
			return "STR";
		}
	},
	DATE{
		@Override
		public String toString() {
			return "DATE";
		}
	},
	TIMESTAMP{
		@Override
		public String toString() {
			return "TIMESTAMP";
		}
	},
	RECORD{
		@Override
		public String toString() {
			return "RECORD";
		}
	},
	EMPTY{
		@Override
		public String toString() {
			return "EMPTY";
		}
	},
	UNKNOWN{
		@Override
		public String toString() {
			return "UNKNOWN";
		}
	};
	
	private static LogElemLabel[] staticLabels = new LogElemLabel[]{
		LogElemLabel.INT,
		LogElemLabel.ID,
		LogElemLabel.STR,
		LogElemLabel.DATE,
		LogElemLabel.TIMESTAMP,
		LogElemLabel.RECORD,
		LogElemLabel.EMPTY,
		LogElemLabel.UNKNOWN,
	};
	
	public static LogElemLabel fromString(String str) {
		for (int i=0; i<staticLabels.length; i++) {
			if (str.equals(staticLabels[i].toString())) {
				return staticLabels[i];
			}
		}
		return null;
	}
	
}
