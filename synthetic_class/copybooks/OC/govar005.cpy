******************************************************************
*  COPYBOOK  : GOVAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : VA
******************************************************************
 01  RT-OVA-RATING.

          03 RT-OVA-TERRITORY-CODE            PIC X(3).
          03 RT-OVA-CLASS-CODE                PIC X(4).
          03 RT-OVA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OVA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OVA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OVA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OVA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OVA-RATED-PREMIUM             PIC 9(9)V9(2).
