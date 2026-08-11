******************************************************************
*  COPYBOOK  : GOSDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : SD
******************************************************************
 01  RT-OSD-RATING.

          03 RT-OSD-TERRITORY-CODE            PIC X(3).
          03 RT-OSD-CLASS-CODE                PIC X(4).
          03 RT-OSD-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OSD-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OSD-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OSD-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OSD-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OSD-RATED-PREMIUM             PIC 9(9)V9(2).
