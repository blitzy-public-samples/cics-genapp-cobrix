******************************************************************
*  COPYBOOK  : GOORR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : OR
******************************************************************
 01  RT-OOR-RATING.

          03 RT-OOR-TERRITORY-CODE            PIC X(3).
          03 RT-OOR-CLASS-CODE                PIC X(4).
          03 RT-OOR-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OOR-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OOR-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OOR-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OOR-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OOR-RATED-PREMIUM             PIC 9(9)V9(2).
