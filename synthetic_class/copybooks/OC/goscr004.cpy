******************************************************************
*  COPYBOOK  : GOSCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : SC
******************************************************************
 01  RT-OSC-RATING.

          03 RT-OSC-TERRITORY-CODE            PIC X(3).
          03 RT-OSC-CLASS-CODE                PIC X(4).
          03 RT-OSC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OSC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OSC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OSC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OSC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OSC-RATED-PREMIUM             PIC 9(9)V9(2).
